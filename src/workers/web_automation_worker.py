import asyncio
import threading
from PyQt6.QtCore import pyqtSignal, pyqtSlot, QThread

from playwright.async_api import async_playwright, Page
from services import AsyncWebAccess
import settings
from src.autotel import BatteriesAlert, LongRides
from src.goto import LateAlert
import time
from ..app.common.config import cfg
class WebAutomationWorker(QThread):
    toast_signal = pyqtSignal(str, str, str)

    late_table_row = pyqtSignal(object)
    batteries_table_row = pyqtSignal(object)
    long_rides_table_row = pyqtSignal(object)
    request_delete_table = pyqtSignal()
    request_connection = pyqtSignal(str)

    open_url_requested = pyqtSignal(str)
    request_pointer_location = pyqtSignal(str)

    def __init__(self,  parent=None):
        super(WebAutomationWorker, self).__init__(parent)
        self.stop_event = asyncio.Event()
        self.running = True

        self._location_condition = threading.Condition()
        self._location_response = None
        self.lock = asyncio.Lock()
    
    @pyqtSlot()
    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._async_main())
        self.loop.close()
    
    async def _async_main(self):
        async with async_playwright() as playwright:
            async with AsyncWebAccess(playwright, settings.playwright_headless, 'edge', 'Default') as self.web_access:
                await self._init_pages()
                print("WebAutomationWorker started")
                await self.stop_event.wait()
                self.stop_event.clear()
                print("WebAutomationWorker initialized") # never reached
                if not self.running:
                    return

                late, batteries_alert, long_rides_alert = self._init_alerts()
                last_run = 0

                while self.running:
                    now = time.time()
                    if now - last_run >= settings.interval:
                        last_run = now
                        await self._run_alert_requests(late, batteries_alert, long_rides_alert)
                    timeout = max(1, settings.interval - (now - last_run))
                    await self.wait_by(timeout=timeout)
                    
    async def wait_by(self, timeout=None):
        try:
            await asyncio.wait_for(self.stop_event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            pass
        self.stop_event.clear()
        
    def trigger_stop_event(self):
        print("Triggering stop_event from signal...")
        if self.loop:
            self.loop.call_soon_threadsafe(self.stop_event.set)
        
    async def _init_pages(self):
        pages_data = {}
        if cfg.get(cfg.late_rides):
            pages_data['goto_bo'] = settings.goto_url

        if cfg.get(cfg.long_rides ) or cfg.get(cfg.batteries):
            pages_data['autotel_bo'] = settings.autotel_url

        self.request_delete_table.emit()
        await self.web_access.create_pages(pages_data)

    def request_pointer_location_sync(self, car_license: str) -> object:
        """Emit signal and wait for location data."""
        self._location_response = None

        with self._location_condition:
            self.request_pointer_location.emit(car_license)
            if not self._location_condition.wait(timeout=30):
                return None
            return self._location_response
            
    def _init_alerts(self):
        late = None
        batteries_alert = None
        long_rides_alert = None
        if cfg.get(cfg.late_rides):
            late = LateAlert(
                show_toast=lambda title, message, icon: self.toast_signal.emit(title, message, icon),
                gui_table_row=lambda row: self.late_table_row.emit(row),
                web_access=self.web_access,
                open_ride=self.open_url_requested
            )
    
        if cfg.get(cfg.batteries):
            batteries_alert = BatteriesAlert(
                show_toast=lambda title, message, icon: self.toast_signal.emit(title, message, icon),
                gui_table_row=lambda row: self.batteries_table_row.emit(row),
                web_access=self.web_access,
                pointer=self.request_pointer_location_sync,
                open_ride=self.open_url_requested
            )
        if cfg.get(cfg.long_rides):
            long_rides_alert = LongRides(
                show_toast=lambda title, message, icon: self.toast_signal.emit(title, message, icon),
                gui_table_row=lambda row: self.long_rides_table_row.emit(row),
                web_access=self.web_access,
                pointer=self.request_pointer_location_sync,
                open_ride=self.open_url_requested,
            )
        
        return late, batteries_alert, long_rides_alert

    async def _run_alert_requests(self, late, batteries_alert, long_rides_alert):
        tasks = []
        if late is not None:
            tasks.append(asyncio.create_task(late.start_requests()))
        if long_rides_alert is not None:
            print("Starting long rides alert requests")
            tasks.append(asyncio.create_task(long_rides_alert.start_requests()))
        if batteries_alert is not None:
            tasks.append(asyncio.create_task(batteries_alert.start_requests()))
        if tasks:
            await asyncio.gather(*tasks)
        
    @pyqtSlot(object)
    def set_location_data(self, data):
        """Receives location data from WebDataWorker."""
        with self._location_condition:
            self._location_response = data
            self._location_condition.notify()

    async def establish_connection(self, page: Page, cta: str):
        while 'login' in page.url:
            self.request_connection.emit(cta)
            await self.stop_event.wait()
            self.stop_event.clear()
            await page.wait_for_load_state('domcontentloaded')
    def stop(self):
        self.running = False
        self.stop_event.set()