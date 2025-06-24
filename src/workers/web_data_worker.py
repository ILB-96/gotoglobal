from queue import Queue
import threading
from PyQt6.QtCore import pyqtSignal, pyqtSlot, QThread

from playwright.async_api import async_playwright
from services import AsyncWebAccess
import settings
from src.shared import PointerLocation
import time
import asyncio
import subprocess
import socket
from ..app.common.config import cfg
class WebDataWorker(QThread):
    page_loaded = pyqtSignal()

    request_otp_input = pyqtSignal()
    input_send = pyqtSignal(object)
    input_received = pyqtSignal(object)
    pointer_location_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super(WebDataWorker, self).__init__(parent)
        self.stop_event = threading.Event()
        self.running = True
        self.url_queue = Queue()
        self.pointer_queue = Queue()
        self.pointer_location_requested.connect(self.enqueue_pointer_location)
        self.code = None

    @pyqtSlot()
    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._async_main())
        loop.close()
    def is_debug_port_open(self, port=9222):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)  # short timeout
            result = sock.connect_ex(('localhost', port))
            return result == 0

    async def _async_main(self):
        # close all edge instances

        if not self.is_debug_port_open():
            subprocess.call(['taskkill', '/F', '/IM', 'msedge.exe'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.call([
                'start', 'msedge', '--remote-debugging-port=9222', '--no-first-run'
            ], shell=True)


        async with async_playwright() as playwright:
            async with AsyncWebAccess(playwright, False, 'edge', 'Default') as self.web_access:
                await self._init_pages()
                pointer = await self._handle_pointer_login() if cfg.get(cfg.pointer) else None
            
                self.page_loaded.emit()
                start_time = 0
                while self.running:
                    await self._handle_url_queue()
                    await self._handle_pointer_location_queue(pointer)
                    
                    if 'blank' in self.web_access.pages.keys() and not self.web_access.pages['blank'].is_closed():
                        await self.web_access.pages['blank'].reload()
                    else:
                        await self.web_access.create_new_page({'blank','about:blank'}, 'reuse')
                    now = time.time()
                    if now - start_time >= settings.interval and pointer:
                        start_time = now
                        await self.web_access.pages["pointer"].reload()
                    self.stop_event.wait(5)
                    self.stop_event.clear()
                    
    async def _init_pages(self):
        pages_data = {}
        if cfg.get(cfg.pointer):
            for page in list(self.web_access.context.pages):
                if page.url == 'https://fleet.pointer4u.co.il/iservices/fleet2015/login':
                    self.web_access.pages['pointer'] = page
                    break
                if 'login' in page.url:
                    await page.close()
            if 'pointer' not in self.web_access.pages.keys():
                pages_data['pointer'] = 'https://fleet.pointer4u.co.il/iservices/fleet2015/login'
                
        if cfg.get(cfg.create_goto_tabs):
            goto_bo = False
            goto_crm = False
            for page in list(self.web_access.context.pages):
                if settings.goto_url in page.url:
                    goto_bo = True
                if settings.goto_crm_url in page.url:
                    goto_crm = True
            if not goto_bo:
                pages_data['goto_bo'] = settings.goto_url
            if not goto_crm:
                pages_data['goto_crm'] = settings.goto_crm_url
        if cfg.get(cfg.create_goto_tabs):
            autotel_bo = False
            autotel_crm = False
            for page in list(self.web_access.context.pages):
                if settings.autotel_url in page.url:
                    autotel_bo = True
                if settings.autotel_crm_url in page.url:
                    autotel_crm = True
            if not autotel_bo:
                pages_data['autotel_bo'] = settings.autotel_url
            if not autotel_crm:
                pages_data['autotel_crm'] = settings.autotel_crm_url
        
        for page in list(self.web_access.context.pages):
            if page.url == 'about:blank':
                self.web_access.pages['blank'] = page
                break
        if 'blank' not in self.web_access.pages.keys():
            pages_data['blank'] = 'about:blank'
                
            
        await self.web_access.create_pages(pages_data)
            
    async def _handle_url_queue(self):
        while not self.url_queue.empty() and self.running:
            try:
                url = self.url_queue.get_nowait()
                page = await self.web_access.context.new_page()
                if settings.goto_url in url:
                    await page.goto(settings.goto_url)
                elif settings.autotel_url in url:
                    await page.goto(settings.autotel_url)
                await page.goto(url)
            except Exception:
                pass
            
    async def _handle_pointer_location_queue(self, pointer: PointerLocation):
        while not self.pointer_queue.empty() and self.running:
            try:
                car_license = self.pointer_queue.get_nowait()
                data = await pointer.search_location(car_license)
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
        pointer = PointerLocation(self.web_access)
        await pointer.login(cfg.get(cfg.pointer_user), cfg.get(cfg.phone))
        while True:
            try:
                await self.web_access.pages["pointer"].wait_for_selector('textarea.realInput', timeout=7000)
                if await self.web_access.pages["pointer"].locator('.confirm').is_visible():
                    await self.web_access.pages["pointer"].locator('.confirm').click()
                self.request_otp_input.emit()
                self.stop_event.wait()
                self.stop_event.clear()
                await pointer.fill_otp(self.code)
                time.sleep(2)
            except Exception:
                del self.code
                break

        return pointer
    
    def set_pointer_code(self, data):
        self.code = data.get('code', None)
        self.stop_event.set()
    
    def stop(self):
        self.running = False
        self.stop_event.set()
    

