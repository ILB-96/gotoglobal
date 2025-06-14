from pathlib import Path
from queue import Queue
import threading
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QRunnable

from playwright.sync_api import sync_playwright
from services import WebAccess
import settings
from src.autotel import BatteriesAlert, LongRides
from src.goto import LateAlert
from src.shared import PointerLocation
import time

class WorkSignals(QObject):
    page_loaded = pyqtSignal(str, int, int, object)
    toast_signal = pyqtSignal(str, str, str)
    
    late_table_row = pyqtSignal(object, tuple)
    batteries_table_row = pyqtSignal(object)
    long_rides_table_row = pyqtSignal(object)
    
    open_url_requested = pyqtSignal(str)
    request_settings_input = pyqtSignal()
    request_otp_input = pyqtSignal()
    input_received = pyqtSignal(object)
    
    start_loading = pyqtSignal()
    stop_loading = pyqtSignal()

class PlaywrightWorker(QRunnable):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.signals = WorkSignals()
        self.stop_event = threading.Event()
        self.running = True
        self.url_queue = Queue()
        self.signals.open_url_requested.connect(self.enqueue_url)
        self.account = {}

    @pyqtSlot()
    def run(self):
        if data := self.db.find_one({'username': Path.home().name}, 'user'):
            self.account = data
        
        self.signals.request_settings_input.emit()
        with sync_playwright() as playwright:
            with WebAccess(playwright, settings.playwright_headless, 'Default') as self.web_access:
                self.stop_event.wait()
                self.stop_event.clear()

                self._init_pages()
                
                pointer = self._handle_pointer_login() if self.account.get('pointer', False) else None
                if not self.running:
                    return

                late, batteries_alert, long_rides_alert = self._init_alerts(pointer)
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

    def _init_pages(self):
        pages_data = {}
        if self.account.get('goto', False):
            pages_data['goto_bo'] = settings.goto_url
        if self.account.get('autotel_bo', False) or self.account.get('batteries', False):
            pages_data['autotel_bo'] = settings.autotel_url
        if self.account.get("pointer", False):
            pages_data['pointer'] = "https://fleet.pointer4u.co.il/iservices/fleet2015/login"
        self.web_access.create_pages(pages_data)


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

    def _handle_pointer_login(self):
        pointer = PointerLocation(self.web_access)
        pointer.login(self.account)
        while True:
            try:
                self.web_access.pages["pointer"].wait_for_selector('textarea.realInput', timeout=7000)
                self.signals.request_otp_input.emit()
                self.stop_event.wait()
                self.stop_event.clear()
                pointer.fill_otp(self.account.get('code', ''))
                time.sleep(2)
            except Exception:
                break

        self.stop_event.wait(5)
        self.stop_event.clear()
        return pointer

    def _init_alerts(self, pointer):
        late = None
        batteries_alert = None
        long_rides_alert = None
        if self.account.get('late_rides', False):
            late = LateAlert(
                self.db,
                show_toast=lambda title, message, icon: self.signals.toast_signal.emit(title, message, icon),
                gui_table_row=lambda row, btn_colors: self.signals.late_table_row.emit(row, btn_colors),
                web_access=self.web_access,
                open_ride=self.signals.open_url_requested
            )
    
        if self.account.get('batteries', False):
            batteries_alert = BatteriesAlert(
                self.db,
                show_toast=lambda title, message, icon: self.signals.toast_signal.emit(title, message, icon),
                gui_table_row=lambda row: self.signals.batteries_table_row.emit(row),
                web_access=self.web_access,
                pointer=pointer,
                open_ride=self.signals.open_url_requested
            )
        if self.account.get('long_rides', False):
            long_rides_alert = LongRides(
                self.db,
                show_toast=lambda title, message, icon: self.signals.toast_signal.emit(title, message, icon),
                gui_table_row=lambda row: self.signals.long_rides_table_row.emit(row),
                web_access=self.web_access,
                pointer=pointer,
                open_ride=self.signals.open_url_requested
            )
        
        return late, batteries_alert, long_rides_alert

    def _run_alert_requests(self, late, batteries_alert, long_rides_alert):
        self.signals.start_loading.emit()
        if late is not None:
            late.start_requests()
        if long_rides_alert is not None:
            long_rides_alert.start_requests()
        if batteries_alert is not None:
            batteries_alert.start_requests()
        self.signals.stop_loading.emit()

    def set_account_data(self, data):
        for key, value in data.items():
            self.account[key] = value
        if 'username' in data:
            self.db.upsert_one(data, 'user')
        self.stop_event.set()

    def enqueue_url(self, url: str):
        self.url_queue.put(url)
        self.stop_event.set()

    def stop(self):
        self.running = False
        self.stop_event.set()