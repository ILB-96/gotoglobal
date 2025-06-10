from pathlib import Path
from queue import Queue
import sys
import threading
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot
from services import TinyDatabase, WebAccess
from playwright.sync_api import sync_playwright
from services import window, popup_window
import settings
from src.frontend import setup_tabs_and_tables, Input, SettingsPanel
from src.shared import PointerLocation
from src.goto import late_alert
from src.autotel import batteries, long_rides

def setup_shared_resources():
    return TinyDatabase({
        "autotel": ["autotelDB.json", "ride_id"],
        "goto": ["gotoDB.json", "ride_id"],
        "user": ["userDB.json", "username"],
    })
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
                    
                if not self.running:
                    return

                long_rides_alert = None
                late = None
                batteries_alert = None
                if self.account.get('late_rides', False):
                    late = late_alert.LateAlert(
                        self.db,
                        show_toast=lambda title, message, icon: self.signals.toast_signal.emit(title, message, icon),
                        gui_table_row=lambda row, btn_colors: self.signals.late_table_row.emit(row, btn_colors),
                        web_access=self.web_access,
                        open_ride=self.signals.open_url_requested
                    )
                if self.account.get('batteries', False):
                    batteries_alert = batteries.BatteriesAlert(
                        self.db,
                        show_toast=lambda title, message, icon: self.signals.toast_signal.emit(title, message, icon),
                        gui_table_row=lambda row: self.signals.batteries_table_row.emit(row),
                        web_access=self.web_access,
                        pointer=pointer,
                        open_ride=self.signals.open_url_requested
                    )
                
                if self.account.get('long_rides', False):
                    long_rides_alert = long_rides.LongRides(
                        self.db,
                        show_toast=lambda title, message, icon: self.signals.toast_signal.emit(title, message, icon),
                        gui_table_row=lambda row: self.signals.long_rides_table_row.emit(row),
                        web_access=self.web_access,
                        pointer=pointer,
                        open_ride=self.signals.open_url_requested
                    )

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

                    if late is not None:
                        late.start_requests()
                    if long_rides_alert is not None:
                        long_rides_alert.start_requests()
                    if batteries_alert is not None:
                        batteries_alert.start_requests()

                    self.stop_event.wait(timeout=7 * 60)
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

def handle_settings_input(worker):
    username = Path.home().name
    cta = f"""
    <h2>Hey {username.replace('.', ' ').title()},</h2>
    <p>
    Welcome to your GOTO service companion!
    <br>
    </p>
    """
    settings_panel = SettingsPanel(account=worker.account)
    popup = popup_window.PopupWindow(
        cta,
        icon=settings.app_icon,
        widgets=[settings_panel]
    )
    data = popup.get_input()
    worker.signals.input_received.emit({ "username": username, **data})
    

def handle_code_input(worker):
    cta = """
    <h2>We need to connect you to Pointer for location data</h2>
    <p>
    Please enter the code sent to your phone number.
    </p>
    """
    line_edit = Input(
        title="code",
        placeholder="Enter 6-digit code",
        validator=r"^\d{6}$",
        error_message="Code must be 6 digits"
    )
    popup = popup_window.PopupWindow(
        cta,
        icon=settings.app_icon,
        widgets=[line_edit],
    )
    data = popup.get_input()
    worker.signals.input_received.emit({ **data })
    
if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        main_win = window.MainWindow(title="GotoGlobal", app_icon=settings.app_icon)
        
        db = setup_shared_resources()
    
        tables = setup_tabs_and_tables(main_win)

        worker = PlaywrightWorker(db)
        # worker.signals.toast_signal.connect(main_win.show_toast)
        # worker.signals.late_table_row.connect(tables['late_rides'].add_rows)
        # worker.signals.batteries_table_row.connect(tables['batteries'].add_rows)
        # worker.signals.long_rides_table_row.connect(tables['long_rides'].add_rows)
        # worker.signals.request_settings_input.connect(lambda: handle_settings_input(worker))
        # worker.signals.request_otp_input.connect(lambda: handle_code_input(worker))
        # worker.signals.input_received.connect(worker.set_account_data)
        

        # main_win.threadpool.start(worker)
        # app.aboutToQuit.connect(worker.stop)
        handle_settings_input(worker)
        # rows = [["12313", "12/12/2023 12:00", ("Future Ride", lambda: print("Open Future Ride")), "12/12/2023 13:00"],
        #         ["12314", "12/12/2023 12:30", ("Future Ride", lambda: print("Open Future Ride")), "12/12/2023 13:30"]]
        
        # tables['late_rides'].add_rows(rows, btn_colors=("#1d5cd0", "#392890", "#1f1f68"))
        # tables['batteries'].add_rows(rows)
        main_win.show()
        sys.exit(app.exec())
    except Exception as e:
        import traceback
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Startup Error")
        msg.setText("An error occurred during startup:")
        msg.setDetailedText(traceback.format_exc())
        msg.exec()
