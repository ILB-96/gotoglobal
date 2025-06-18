from pathlib import Path
from queue import Queue
import threading
from PyQt6.QtCore import pyqtSignal, pyqtSlot, QThread

from playwright.sync_api import sync_playwright
from services import WebAccess
import settings
from src.autotel import BatteriesAlert, LongRides
from src.goto import LateAlert
from src.shared import PointerLocation, User
import time

class WebAutomationWorker(QThread):
    toast_signal = pyqtSignal(str, str, str)

    late_table_row = pyqtSignal(object, tuple)
    batteries_table_row = pyqtSignal(object)
    long_rides_table_row = pyqtSignal(object)
    request_delete_table = pyqtSignal(str, str)
    request_delete_tab = pyqtSignal(str)

    open_url_requested = pyqtSignal(str)
    request_otp_input = pyqtSignal()
    input_received = pyqtSignal(object)
    request_pointer_location = pyqtSignal(str)

    start_loading = pyqtSignal()
    stop_loading = pyqtSignal()
    def __init__(self, account: User, parent=None):
        super(WebAutomationWorker, self).__init__(parent)
        self.stop_event = threading.Event()
        self.running = True
        self.url_queue = Queue()
        self.open_url_requested.connect(self.enqueue_url)
        self.account = account
        self._location_condition = threading.Condition()
        self._location_response = None

    @pyqtSlot()
    def run(self):
        with sync_playwright() as playwright:
            with WebAccess(playwright, settings.playwright_headless, 'chrome', 'Default') as self.web_access:
                self._init_pages()
                
                # pointer = self._handle_pointer_login() if self.account.pointer else None
                print("WebAutomationWorker started")
                self.stop_event.wait()
                self.stop_event.clear()
                if not self.running:
                    return
                print("WebAutomationWorker initialized")

                late, batteries_alert, long_rides_alert = self._init_alerts()
                last_run = 0

                while self.running:
                    self._handle_url_queue()
                    now = time.time()
                    if now - last_run >= settings.interval:
                        self._run_alert_requests(late, batteries_alert, long_rides_alert)
                        last_run = now
                    timeout = max(1, settings.interval - (now - last_run))
                    self.stop_event.wait(timeout=timeout)
                    self.stop_event.clear()
                
                if self.account is not None:
                    self.account.to_json(settings.user_json_path)
                    
    def enqueue_pointer_location(self, query: str):
        self.request_pointer_location.emit(query)
        self.stop_event.wait()
        self.stop_event.clear()
        
    def _init_pages(self):
        pages_data = {}
        if self.account.late_rides:
            pages_data['goto_bo'] = settings.goto_url
        else:
            self.request_delete_tab.emit('Goto')
        if self.account.long_rides or self.account.batteries:
            pages_data['autotel_bo'] = settings.autotel_url
            if not self.account.long_rides:
                self.request_delete_table.emit('Autotel', 'Long Rides')
            if not self.account.batteries:
                self.request_delete_table.emit('Autotel', 'Batteries')
        else:
            self.request_delete_tab.emit('Autotel')
        if self.account.pointer:
            pages_data['pointer'] = "https://fleet.pointer4u.co.il/iservices/fleet2015/login"
        self.web_access.create_pages(pages_data)

    def request_pointer_location_sync(self, car_license: str) -> object:
        """Emit signal and wait for location data."""
        self._location_response = None

        with self._location_condition:
            self.request_pointer_location.emit(car_license)
            if not self._location_condition.wait(timeout=10):
                print("Timed out waiting for pointer location")
                return None  # Timeout fallback
            return self._location_response
    def _handle_url_queue(self):
        while not self.url_queue.empty() and self.running:
            try:
                url = self.url_queue.get_nowait()
                page = self.web_access.context.new_page()
                if settings.goto_url in url:
                    page.goto(settings.goto_url)
                elif settings.autotel_url in url:
                    page.goto(settings.autotel_url)
                page.goto(url)
            except Exception:
                pass
            
    @pyqtSlot(object)
    def set_location_data(self, data):
        """Receives location data from WebDataWorker."""
        print(f"Received location data: {data}")
        with self._location_condition:
            self._location_response = data
            self._location_condition.notify()
            
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
        self.start_loading.emit()
        if late is not None:
            late.start_requests()
        if long_rides_alert is not None:
            long_rides_alert.start_requests()
        if batteries_alert is not None:
            batteries_alert.start_requests()
        self.stop_loading.emit()

    def set_account_data(self, data):
        self.account.update(**data)
        self.account.to_json(settings.user_json_path)
        self.stop_event.set()

    def enqueue_url(self, url: str):
        self.url_queue.put(url)
        self.stop_event.set()

    def stop(self):
        self.running = False
        self.stop_event.set()