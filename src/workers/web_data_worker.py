from queue import Queue
import threading
from PyQt6.QtCore import pyqtSignal, pyqtSlot, QThread

from playwright.async_api import async_playwright
from services import AsyncWebAccess
from services.web_access_service.file_mover import FileMover
import settings
from src.shared import PointerLocation, utils
import time
import asyncio
import subprocess
import socket
import win32gui
import win32con
from ..app.common.config import cfg
class WebDataWorker(QThread):
    page_loaded = pyqtSignal()

    request_otp_input = pyqtSignal()
    input_send = pyqtSignal(object)
    input_received = pyqtSignal()
    pointer_location_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super(WebDataWorker, self).__init__(parent)
        self.stop_event = asyncio.Event()
        self.running = True
        self.url_queue = Queue()
        self.pointer_queue = Queue()
        self.pointer_location_requested.connect(self.enqueue_pointer_location)
        self.pointer_lock = asyncio.Lock()
        self.pointer = None


    @pyqtSlot()
    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._async_main())
        loop.close()
    def is_debug_port_open(self, port=9222):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            return result == 0

    async def _async_main(self):

        if not self.is_debug_port_open():
            subprocess.call(['taskkill', '/F', '/IM', 'msedge.exe'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.call([
                'start', 'msedge', '--remote-debugging-port=9222', '--no-first-run'
            ], shell=True)


        async with async_playwright() as playwright:
            async with AsyncWebAccess(playwright, False, 'edge', 'Port') as self.web_access:
                await self._init_pages()
                
                asyncio.create_task(self._handle_pointer_login()) if cfg.get(cfg.pointer) else self.page_loaded.emit()
                file_mover = FileMover()
                start_time = 0
                while self.running:
                    await self._handle_url_queue()
                    await self._handle_pointer_location_queue()
                    asyncio.create_task(self.update_page_data())
                    file_mover.move_files()
                    now = time.time()
                    if self.pointer and now - start_time >= settings.interval: 
                        start_time = now
                        asyncio.create_task(self.reload_pointer_data())
                    await self.wait_by(timeout=5)
                
    async def wait_by(self, timeout=None):
        try:
            await asyncio.wait_for(self.stop_event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            pass
        self.stop_event.clear()

    async def reload_pointer_data(self):
        async with self.pointer_lock:
            await self.web_access.pages["pointer"].reload()

    @utils.retry(allow_falsy=True)
    async def update_page_data(self):
        if 'blank' in self.web_access.pages.keys() and not self.web_access.pages['blank'].is_closed():
            await self.web_access.pages['blank'].reload()
        else:
            await self.web_access.create_new_page('blank','about:blank', 'reuse')
                    
    async def _init_pages(self):
        pages_to_create = {}
        pointer_url = 'https://fleet.pointer4u.co.il/iservices/fleet2015/login'
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
            self.bring_window_to_front('Work')
            if targets['pointer'] and page.url == targets['pointer']:
                if await page.locator('textarea.realInput').is_visible():
                    await page.close()
                else:
                    self.web_access.pages['pointer'] = page
                    targets['pointer'] = None
            elif targets['blank'] and page.url == targets['blank']:
                self.web_access.pages['blank'] = page
                targets['blank'] = None
            elif 'login' in page.url or 'about:blank' in page.url or 'pointer4u' in page.url:
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

        await self.web_access.create_pages(pages_to_create)
        if 'pointer' in self.web_access.pages.keys():
            await self.web_access.pages['pointer'].bring_to_front()
            
    async def _handle_url_queue(self):
        while not self.url_queue.empty() and self.running:
            url = self.url_queue.get_nowait()
            asyncio.create_task(self.process_url(url))

    async def process_url(self, url):
        try:
            self.bring_window_to_front('Work')
            page = await self.web_access.context.new_page()
            if settings.goto_url in url:
                await page.goto(settings.goto_url, wait_until='domcontentloaded')
            elif settings.autotel_url in url:
                await page.goto(settings.autotel_url, wait_until='domcontentloaded')
            await page.goto(url, wait_until='domcontentloaded')
            await page.bring_to_front()
            await page.wait_for_function('document.title.length > 0')
            if page.url != 'url':
                await page.goto(url)

        except Exception:
            pass
        

    def bring_window_to_front(self, window_title: str):
        def enumHandler(hwnd, lParam):
            if win32gui.IsWindowVisible(hwnd):
                if window_title.lower() in win32gui.GetWindowText(hwnd).lower():
                    placement = win32gui.GetWindowPlacement(hwnd)
                    # Only restore if minimized
                    if placement[1] == win32con.SW_SHOWMINIMIZED:
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    try:
                        win32gui.SetForegroundWindow(hwnd)
                    except Exception as e:
                        print(f"Could not bring window to front: {e}")
        win32gui.EnumWindows(enumHandler, None)
                    
    async def _handle_pointer_location_queue(self):
        async with self.pointer_lock:
            if not self.pointer:
                return
            while not self.pointer_queue.empty() and self.running:
                try:
                    car_license = self.pointer_queue.get_nowait()
                    data = await self.pointer.search_location(car_license)
                    self.input_send.emit(data.strip("").strip(","))
                except Exception:
                    pass
    def enqueue_url(self, url: str):
        """Enqueue a URL to be opened in the web access context."""
        if not self.running:
            return
        self.url_queue.put(url)
        self.stop_event.set()

    def enqueue_pointer_location(self, location: str):
        """Enqueue a pointer location request."""
        if not self.running:
            return
        self.pointer_queue.put(location)
        self.stop_event.set()
        
    async def _handle_pointer_login(self):
        async with self.pointer_lock:
            self.pointer = PointerLocation(self.web_access)
            await self.pointer.login(cfg.get(cfg.pointer_user), cfg.get(cfg.phone))
            while self.running:
                try:
                    await self.web_access.pages["pointer"].wait_for_selector('textarea.realInput', timeout=7000)
                    if await self.web_access.pages["pointer"].locator('.confirm').is_visible():
                        await self.web_access.pages["pointer"].locator('.confirm').click()
                    self.request_otp_input.emit()
                    await self.stop_event.wait()
                    self.stop_event.clear()
                    # if not self.code:
                    #     raise Exception("No code provided")
                    # await self.pointer.fill_otp(self.code)
                    # await asyncio.sleep(2)
                except Exception:
                    # del self.code
                    print("Pointer logged in successfully")
                    self.page_loaded.emit()
                    break

    
    def set_pointer_code(self):
        self.stop_event.set()
    
    def stop(self):
        self.running = False
        self.stop_event.set()