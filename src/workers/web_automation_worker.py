import asyncio
import threading
from typing import Literal
from PyQt6.QtCore import pyqtSignal, pyqtSlot, QThread

from playwright.async_api import async_playwright
import settings
from src.autotel import BatteriesAlert, LongRides
from src.goto import LateAlert
import time
from ..app.common.config import cfg
from .base_worker import BaseWorker

class WebAutomationWorker(BaseWorker):
    toast_signal = pyqtSignal(str, str, str)

    late_table_row = pyqtSignal(object)
    batteries_table_row = pyqtSignal(object)
    long_rides_table_row = pyqtSignal(object)
    request_delete_table = pyqtSignal()
    request_connection = pyqtSignal(str)

    open_url_requested = pyqtSignal(str)
    request_pointer_location = pyqtSignal(str)
    request_x_token = pyqtSignal(str)

    def __init__(self,  parent=None):
        super(WebAutomationWorker, self).__init__(parent)

        self._location_condition = threading.Condition()
        self._location_response = None

        self._x_token_condition = threading.Condition()
        self._goto_x_token = None
        self._autotel_x_token = None

    
    async def _async_main(self):
        self.request_delete_table.emit()
        await self.stop_event.wait()
        self.stop_event.clear()

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
                    
        
    def request_x_token_sync(self, mode: Literal['goto', 'autotel']) -> object:
        """Emit signal and wait for location data."""
        if mode == 'goto':
            self._goto_x_token = None
        elif mode == 'autotel':
            self._autotel_x_token = None
        with self._x_token_condition:
            self.request_x_token.emit(mode)
            if not self._x_token_condition.wait(timeout=70):
                return
        
        return self._goto_x_token if mode == 'goto' else self._autotel_x_token
        
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
                open_ride=self.open_url_requested,
                x_token_request=self.request_x_token_sync,
            )
    
        if cfg.get(cfg.batteries):
            batteries_alert = BatteriesAlert(
                show_toast=lambda title, message, icon: self.toast_signal.emit(title, message, icon),
                gui_table_row=lambda row: self.batteries_table_row.emit(row),
                pointer=self.request_pointer_location_sync,
                open_ride=self.open_url_requested,
                x_token_request=self.request_x_token_sync
            )
        if cfg.get(cfg.long_rides):
            long_rides_alert = LongRides(
                show_toast=lambda title, message, icon: self.toast_signal.emit(title, message, icon),
                gui_table_row=lambda row: self.long_rides_table_row.emit(row),
                pointer=self.request_pointer_location_sync,
                open_ride=self.open_url_requested,
                x_token_request=self.request_x_token_sync
            )
        
        return late, batteries_alert, long_rides_alert

    async def _run_alert_requests(self, late, batteries_alert, long_rides_alert):
        tasks = []
        if late is not None:
            tasks.append(asyncio.create_task(late.start_requests(self._goto_x_token)))
        if long_rides_alert is not None:
            tasks.append(asyncio.create_task(long_rides_alert.start_requests(self._autotel_x_token)))
        if batteries_alert is not None:
            tasks.append(asyncio.create_task(batteries_alert.start_requests(self._autotel_x_token)))
        if tasks:
            await asyncio.gather(*tasks)
    
    
    @pyqtSlot(object)
    def set_x_token_data(self, mode, data):
        """Receives location data from WebDataWorker."""
        with self._x_token_condition:
            if mode == 'goto':
                self._goto_x_token = data
            elif mode == 'autotel':
                self._autotel_x_token = data
            self._x_token_condition.notify()
            
    @pyqtSlot(object)
    def set_location_data(self, data):
        """Receives location data from WebDataWorker."""
        with self._location_condition:
            self._location_response = data
            self._location_condition.notify()
            