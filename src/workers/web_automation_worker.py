import threading
from PyQt6.QtCore import pyqtSignal, pyqtSlot, QThread

from playwright.sync_api import sync_playwright
from services import WebAccess
import settings
from src.autotel import BatteriesAlert, LongRides
from src.goto import LateAlert
from src.shared import User
import time

class WebAutomationWorker(QThread):
    toast_signal = pyqtSignal(str, str, str)

    late_table_row = pyqtSignal(object, tuple)
    batteries_table_row = pyqtSignal(object)
    long_rides_table_row = pyqtSignal(object)
    request_delete_table = pyqtSignal(object)
    request_delete_tab = pyqtSignal(str)

    open_url_requested = pyqtSignal(str)
    request_pointer_location = pyqtSignal(str)

    def __init__(self, account: User, parent=None):
        super(WebAutomationWorker, self).__init__(parent)
        self.stop_event = threading.Event()
        self.running = True

        self.account = account
        self._location_condition = threading.Condition()
        self._location_response = None

    @pyqtSlot()
    def run(self):
        with sync_playwright() as playwright:
            with WebAccess(playwright, settings.playwright_headless, 'chrome', 'Default') as self.web_access:
                self._init_pages()
                
                self.stop_event.wait()
                self.stop_event.clear()
                if not self.running:
                    return

                late, batteries_alert, long_rides_alert = self._init_alerts()
                last_run = 0

                while self.running:
                    now = time.time()
                    if now - last_run >= settings.interval:
                        self._run_alert_requests(late, batteries_alert, long_rides_alert)
                        last_run = now
                    timeout = max(1, settings.interval - (now - last_run))
                    self.stop_event.wait(timeout=timeout)
                    self.stop_event.clear()
                
                    
    def enqueue_pointer_location(self, query: str):
        self.request_pointer_location.emit(query)
        self.stop_event.wait()
        self.stop_event.clear()
        
    def _init_pages(self):
        pages_data = {}
        if self.account.late_rides:
            pages_data['goto_bo'] = settings.goto_url
        # else:
        #     self.request_delete_tab.emit('Goto')
        if self.account.long_rides or self.account.batteries:
            pages_data['autotel_bo'] = settings.autotel_url
            # if not self.account.long_rides:
            #     self.request_delete_table.emit('Autotel', 'Long Rides')
            # if not self.account.batteries:
            #     self.request_delete_table.emit('Autotel', 'Batteries')
        # else:
        #     self.request_delete_tab.emit('Autotel')
        self.request_delete_table.emit(self.account)
        self.web_access.create_pages(pages_data)

    def request_pointer_location_sync(self, car_license: str) -> object:
        """Emit signal and wait for location data."""
        self._location_response = None

        with self._location_condition:
            self.request_pointer_location.emit(car_license)
            if not self._location_condition.wait(timeout=30):
                return None
            return self._location_response
            
    def _init_alerts(self, pointer=None):
        late = None
        batteries_alert = None
        long_rides_alert = None
        if self.account.late_rides:
            late = LateAlert(
                show_toast=lambda title, message, icon: self.toast_signal.emit(title, message, icon),
                gui_table_row=lambda row, btn_colors: self.late_table_row.emit(row, btn_colors),
                web_access=self.web_access,
                open_ride=self.open_url_requested
            )
    
        if self.account.batteries:
            batteries_alert = BatteriesAlert(
                show_toast=lambda title, message, icon: self.toast_signal.emit(title, message, icon),
                gui_table_row=lambda row: self.batteries_table_row.emit(row),
                web_access=self.web_access,
                pointer=self.request_pointer_location_sync,
                open_ride=self.open_url_requested
            )
        if self.account.long_rides:
            long_rides_alert = LongRides(
                show_toast=lambda title, message, icon: self.toast_signal.emit(title, message, icon),
                gui_table_row=lambda row: self.long_rides_table_row.emit(row),
                web_access=self.web_access,
                pointer=self.request_pointer_location_sync,
                open_ride=self.open_url_requested,
            )
        
        return late, batteries_alert, long_rides_alert

    def _run_alert_requests(self, late, batteries_alert, long_rides_alert):
        if late is not None:
            late.start_requests()
        if long_rides_alert is not None:
            long_rides_alert.start_requests()
        if batteries_alert is not None:
            batteries_alert.start_requests()

    def set_account_data(self, data):
        self.account.update(**data)
        self.account.to_json(settings.user_json_path)
        self.stop_event.set()
        
    @pyqtSlot(object)
    def set_location_data(self, data):
        """Receives location data from WebDataWorker."""
        print(f"Received location data: {data}")
        with self._location_condition:
            self._location_response = data
            self._location_condition.notify()

    def stop(self):
        self.running = False
        self.stop_event.set()