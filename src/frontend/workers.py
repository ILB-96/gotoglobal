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
        # else:
        self.signals.request_settings_input.emit()
        with sync_playwright() as playwright:
            with WebAccess(playwright, settings.playwright_headless, 'Default') as self.web_access:
                self.web_access.create_pages({
                    "goto_bo": "https://car2gobo.gototech.co",
                    "autotel_bo": "https://prodautotelbo.gototech.co",
                    "pointer": "https://fleet.pointer4u.co.il/iservices/fleet2015/login"
                })
                self.stop_event.wait()
                self.stop_event.clear()
                pointer = None
                if self.account.get('pointer', False):
                    self.signals.request_otp_input.emit()
                
                    pointer = PointerLocation(self.web_access, self.account)
                
                    self.stop_event.wait()
                    self.stop_event.clear()
                    
                    pointer.fill_otp(self.account.get('code', ''))
                    self.stop_event.wait(5)
                    self.stop_event.clear()
                    
                if not self.running:
                    return

                long_rides_alert = None
                late = None
                batteries_alert = None
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

                last_run = 0
                interval = 5 * 60

                while self.running:
                    while not self.url_queue.empty() and self.running:
                        try:
                            url = self.url_queue.get_nowait()
                            page = self.web_access.context.new_page()
                            if settings.goto_url in url:
                                page.goto(settings.goto_url)
                            elif settings.autotel_url in url:
                                page.goto(settings.autotel_url)
                            page.goto(url)
                        except Exception as e:
                            pass

                    now = time.time()
                    if now - last_run >= interval:
                        if late is not None:
                            late.start_requests()
                        if long_rides_alert is not None:
                            long_rides_alert.start_requests()
                        if batteries_alert is not None:
                            batteries_alert.start_requests()
                        last_run = now

                    # Wait for a short time to avoid busy loop, but wake up if stop_event is set
                    timeout = max(1, interval - (now - last_run))
                    self.stop_event.wait(timeout=timeout)
                    self.stop_event.clear()


    def set_account_data(self, data):
        for key, value in data.items():
            self.account[key] = value
        if 'username' in data:
            self.db.upsert_one(
                data,
                'user'
            )

        self.stop_event.set()
    
    def enqueue_url(self, url: str):
        self.url_queue.put(url)
        self.stop_event.set()
    
    def stop(self):
        self.running = False
        self.stop_event.set()