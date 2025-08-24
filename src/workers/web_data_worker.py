import json
from queue import Queue
from PyQt6.QtCore import pyqtSignal

from playwright.async_api import Request, Page
from services import AsyncWebAccess
import settings
from src.shared import PointerLocation, utils
import time
import asyncio

import win32gui
import win32con
import ctypes

from .base_worker import BaseWorker
from ..app.common.config import cfg
from dataclasses import dataclass
from typing import Literal, Union

@dataclass
class WebTask:
    mode: Literal["url", "pointer", "x_token", "cookies"]
    payload: Union[str, int, Literal['goto', 'autotel']]
    
class WebDataWorker(BaseWorker):
    page_loaded = pyqtSignal()
    notification_send = pyqtSignal(str, object)

    request_otp_input = pyqtSignal()
    pointer_location_send = pyqtSignal(object)
    x_token_send = pyqtSignal(str, str)
    input_received = pyqtSignal()
    cookies_send = pyqtSignal(str, str)
    
    
    def __init__(self, parent=None):
        super(WebDataWorker, self).__init__(parent)
        self.task_queue = Queue()
        self.pointer_lock = asyncio.Lock()
        self.pointer = None

 
    async def _async_main(self):
        async with AsyncWebAccess(False, 'edge', 'Port') as self.web_access:
            await self._init_pages()
            
            asyncio.create_task(self._handle_pointer_login()) if cfg.get(cfg.pointer) else self.page_loaded.emit()
            await self.start_notification_listeners()
            start_time = 0
            reload_blank_page = None
            while self.running:
                await self._handle_queue()
                if reload_blank_page:
                    await reload_blank_page
                reload_blank_page = asyncio.create_task(self.update_page_data())
                now = time.time()
                if self.pointer and now - start_time >= settings.pointer_interval:
                    start_time = now
                    asyncio.create_task(self.reload_pointer_data())
                await self.wait_by(timeout=3)

    @utils.async_retry(allow_falsy=True)
    async def reload_pointer_data(self):
        async with self.pointer_lock:
            await self.web_access.pages["pointer"].reload()

    @utils.async_retry(allow_falsy=True)
    async def update_page_data(self):
        await self.web_access.create_new_page('blank','about:blank', 'reuse')
                    
    async def _init_pages(self):
        pages_to_create = {}
        pointer_url = 'https://fleet.pointer4u.co.il/iservices/fleet2015'
        autotel_crm_url = 'https://autotel.crm4.dynamics.com'
        goto_crm_url = 'https://goto.crm4.dynamics.com'
        whatsapp_url = 'https://web.whatsapp.com'
        targets = {'blank': 'about:blank',
                'pointer': pointer_url if cfg.get(cfg.pointer) else None,
                'goto_bo': settings.goto_url if cfg.get(cfg.create_goto_tabs) else None,
                'goto_crm': goto_crm_url if cfg.get(cfg.create_goto_tabs) else None,
                'autotel_bo': settings.autotel_url if cfg.get(cfg.create_autotel_tabs) else None,
                'autotel_crm': autotel_crm_url if cfg.get(cfg.create_autotel_tabs) else None,
                'whatsapp':  whatsapp_url if cfg.get(cfg.create_whatsapp_page) else None,
                }
        
        for page in list(self.web_access.context.pages):
            if targets['pointer'] and page.url == f"{targets['pointer']}/login":
                if await page.locator('textarea.realInput').is_visible():
                    await page.close()
                else:
                    self.web_access.pages['pointer'] = page
                    targets['pointer'] = None
            elif targets['pointer'] and targets['pointer'] in page.url:
                await page.reload()
                self.web_access.pages['pointer'] = page
                targets['pointer'] = None
            elif targets['blank'] and page.url == targets['blank']:
                self.web_access.pages['blank'] = page
                targets['blank'] = None
            elif 'login' in page.url or 'about:blank' in page.url:
                await page.close()
            elif targets['goto_bo'] and targets['goto_bo'] in page.url:
                self.web_access.pages['goto_bo'] = page
                targets['goto_bo'] = None
            elif targets['goto_crm'] and targets['goto_crm'] in page.url:
                self.web_access.pages['goto_crm'] = page
                targets['goto_crm'] = None
            elif targets['autotel_bo'] and targets['autotel_bo'] in page.url:
                self.web_access.pages['autotel_bo'] = page
                targets['autotel_bo'] = None
            elif targets['autotel_crm'] and targets['autotel_crm'] in page.url:
                self.web_access.pages['autotel_crm'] = page
                targets['autotel_crm'] = None
            elif targets['whatsapp'] and targets['whatsapp'] in page.url:
                self.web_access.pages['whatsapp'] = page
                targets['whatsapp'] = None


        pages_to_create = {key: url for key, url in targets.items() if url}
        self.bring_window_to_front('Work - ')
        await self.web_access.create_pages(pages_to_create)
        if 'pointer' in self.web_access.pages.keys():
            await self.web_access.pages['pointer'].bring_to_front()
        
    async def _handle_queue(self):
        tasks = []
        try:
            while not self.task_queue.empty() and self.running:
                task: WebTask = self.task_queue.get_nowait()
                if task.mode == "url":
                    tasks.append(asyncio.create_task(self._handle_open_url_request(task.payload)))
                elif task.mode == "pointer":
                    tasks.append(asyncio.create_task(self._handle_pointer_location_request(str(task.payload))))
                elif task.mode == "x_token":
                    if isinstance(task.payload, str) and task.payload in ('goto', 'autotel'):
                        tasks.append(asyncio.create_task(self._handle_x_token_request(task.payload)))
                elif task.mode == "cookies":
                    if isinstance(task.payload, str) and task.payload in ('goto', 'autotel'):
                        tasks.append(asyncio.create_task(self.handle_cookies_request(task.payload)))

            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    print(f"Error handling task: {result}")

        finally:
            for item in tasks:
                if not item.done():
                    item.cancel()
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
    async def handle_cookies_request(self, mode: Literal['goto', 'autotel']):
        try:
            if mode == 'goto':
                page = await self.find_page("goto_crm", settings.goto_crm_url)
            elif mode == 'autotel':
                page = await self.find_page("autotel_crm", settings.autotel_crm_url)
            else:
                return
            cookies = await self.get_cookies(page)
            self.cookies_send.emit(mode, cookies)
        except Exception as e:
            print(f"Error getting cookies: {e}")
            
    async def _handle_open_url_request(self, url):
        try:
            self.bring_window_to_front('Work - ')
            await asyncio.sleep(0.25)
            page = await self.web_access.context.new_page()
            if settings.goto_url in url:
                await page.goto(settings.goto_url, wait_until='domcontentloaded')
            elif settings.autotel_url in url:
                await page.goto(settings.autotel_url, wait_until='domcontentloaded')
            await page.goto(url, wait_until='domcontentloaded')
            await page.bring_to_front()
            await page.wait_for_function('document.title.length > 0')
            if page.url != url:
                await page.goto(url)
        except Exception:
            pass

    def bring_window_to_front(self, window_title: str):
        def enumHandler(hwnd, lParam):
            if win32gui.IsWindowVisible(hwnd):
                if window_title.lower() in win32gui.GetWindowText(hwnd).lower():
                    placement = win32gui.GetWindowPlacement(hwnd)
                    if placement[1] == win32con.SW_SHOWMINIMIZED:
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    try:
                        ctypes.windll.user32.AllowSetForegroundWindow(-1)
                        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                        win32gui.SetForegroundWindow(hwnd)
                    except Exception as e:
                        print(f"Could not bring window to front: {e}")
        win32gui.EnumWindows(enumHandler, None)
        
                    
    async def _handle_x_token_request(self, mode: Literal['goto', 'autotel']):
        try:
            if mode == 'goto':
                request_page = await self.find_page("goto_bo", settings.goto_url)
            elif mode == 'autotel':
                request_page = await self.find_page("autotel_bo", settings.autotel_url)
            else:
                return
            x_token = await self.get_x_token_from_request(request_page)
            self.x_token_send.emit(mode, x_token)
        except Exception:
            self.x_token_send.emit(mode, None)

    async def find_page(self, name, url) -> Page:
        if name in self.web_access.pages and not self.web_access.pages[name].is_closed:
            return self.web_access.pages[name]
        for page in self.web_access.context.pages:
            if 'login' not in page.url and page.url.startswith(url):
                return page
        return await self.web_access.create_new_page(name, url, open_mode='reuse')
    
    async def _handle_pointer_location_request(self, car_license: str):
        async with self.pointer_lock:
            if not self.pointer:
                return
            try:
                data = await self.pointer.search_location(car_license)
                self.pointer_location_send.emit(data.strip("").strip(","))
            except Exception:
                self.pointer_location_send.emit("Error: Manually reload Pointer")
                
    def enqueue_url(self, url: str):
        """Enqueue a URL to be opened in the web access context."""
        task = WebTask(mode="url", payload=url)
        self.task_queue.put(task)
        self.stop_event.set()
        
    def enqueue_x_token(self, mode: Literal['goto', 'autotel']):
        """Enqueue a pointer location request."""
        print(f"Enqueuing x_token request for mode: {mode}")
        task = WebTask(mode="x_token", payload=mode)
        self.task_queue.put(task)
        self.stop_event.set()
        
    def enqueue_cookies(self, mode: Literal['goto', 'autotel']):
        """Enqueue a request to get cookies from the current page."""
        task = WebTask(mode="cookies", payload=mode)
        self.task_queue.put(task)
        self.stop_event.set()

    def enqueue_pointer_location(self, car_license: str):
        """Enqueue a pointer location request."""
        task = WebTask(mode="pointer", payload=car_license)
        self.task_queue.put(task)
        self.stop_event.set()
        
    async def _handle_pointer_login(self):
        async with self.pointer_lock:
            self.pointer = PointerLocation(self.web_access)
            if 'login' in self.web_access.pages['pointer'].url:
                await self.pointer.login(cfg.get(cfg.pointer_user), cfg.get(cfg.phone))
            while self.running:
                try:
                    await self.web_access.pages["pointer"].wait_for_selector('textarea.realInput', timeout=7000)
                    if await self.web_access.pages["pointer"].locator('.confirm').is_visible():
                        await self.web_access.pages["pointer"].locator('.confirm').click()
                    self.request_otp_input.emit()
                    await self.event_wait()
                except Exception:
                    self.page_loaded.emit()
                    break


    async def get_x_token_from_request(self, page: Page):
        
        credentials = await page.evaluate("""
            () => sessionStorage.getItem('ngStorage-credentials')
        """)
        
        if not credentials:
            return None
        credentials = json.loads(credentials) 
        x_token_value = credentials.get('token', None)

        return x_token_value
    
    async def get_crm_notification(self, page: Page, request_url: str):

        async def handle_request(request: Request):
            if request.method == "GET" and request.url.startswith(request_url):
                if resp := await request.response():
                    data = await resp.json()
                    notifications = data.get("value", [])
                    mode = 'goto' if 'goto' in request.url else 'autotel'
                    print("notification: ", notifications)
                    for item in notifications:
                        self.notification_send.emit(mode, item)

        page.on("request", handle_request)
        
    async def start_notification_listeners(self):
        goto_page = await self.find_page("goto_crm", settings.goto_crm_url)
        autotel_page = await self.find_page("autotel_crm", settings.autotel_crm_url)
        await self.get_crm_notification(goto_page, 'https://goto.crm4.dynamics.com/api/data/v9.0/appnotifications')
        await self.get_crm_notification(autotel_page, 'https://autotel.crm4.dynamics.com/api/data/v9.0/appnotifications')
        
    async def get_cookies(self, page: Page):
        cookie_data = ""
        url = page.url
        cookies = await page.context.cookies([url])
        for cookie in cookies:
            name, val = cookie.get('name', ''), cookie.get('value')
            if name == "CrmOwinAuth":
                cookie_data += f"{name}={val};"
            if name == 'CrmOwinAuthC1':
                cookie_data += f"{name}={val};"
            if name == 'CrmOwinAuthC2':
                cookie_data += f"{name}={val};"
        return cookie_data
        
        
    async def get_page(self, name: str, url: str) -> Page:
        """Get or create a page with the specified name and URL."""
        if name in self.web_access.pages and not self.web_access.pages[name].is_closed:
            return self.web_access.pages[name]
        for page in self.web_access.context.pages:
            if 'login' not in page.url and page.url.startswith(url):
                return page
        return await self.web_access.create_new_page(name, url, open_mode='reuse')

    
