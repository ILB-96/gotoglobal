from queue import Queue
import threading
from PyQt6.QtCore import pyqtSignal, pyqtSlot, QThread

from playwright.async_api import async_playwright
from services import AsyncWebAccess
import settings
from src.shared import PointerLocation, User
import time
import asyncio

class WebDataWorker(QThread):
    page_loaded = pyqtSignal()

    request_otp_input = pyqtSignal()
    input_send = pyqtSignal(object)
    input_received = pyqtSignal(object)
    pointer_location_requested = pyqtSignal(str)

    def __init__(self, account: User, parent=None):
        super(WebDataWorker, self).__init__(parent)
        self.stop_event = threading.Event()
        self.running = True
        self.url_queue = Queue()
        self.pointer_queue = Queue()
        self.pointer_location_requested.connect(self.enqueue_pointer_location)
        self.account = account

    @pyqtSlot()
    def run(self):
        asyncio.run(self._async_main())

    async def _async_main(self):
        async with async_playwright() as playwright:
            async with AsyncWebAccess(playwright, False, 'edge', 'Default') as self.web_access:
                await self._init_pages()
                pointer = await self._handle_pointer_login() if self.account.pointer else None
            
                self.page_loaded.emit()
                start_time = 0
                while self.running:
                    await self._handle_url_queue()
                    await self._handle_pointer_location_queue(pointer)
                    now = time.time()
                    if now - start_time >= settings.interval and pointer:
                        start_time = now
                        await self.web_access.pages["pointer"].reload()
                    self.stop_event.wait(5*60)
                    self.stop_event.clear()
                    
    async def _init_pages(self):
        if self.account.pointer:
            await self.web_access.create_pages({
                'pointer': 'https://fleet.pointer4u.co.il/iservices/fleet2015/login'
            })
            
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
        await pointer.login(self.account.pointer_user, self.account.phone)
        while True:
            try:
                await self.web_access.pages["pointer"].wait_for_selector('textarea.realInput', timeout=7000)
                self.request_otp_input.emit()
                self.stop_event.wait()
                self.stop_event.clear()
                await pointer.fill_otp(self.account.code)
                time.sleep(2)
            except Exception:
                break

        return pointer
    
    def set_account_data(self, data):
        self.account.update(**data)
        self.stop_event.set()
    
    def stop(self):
        self.running = False
        self.stop_event.set()
    

