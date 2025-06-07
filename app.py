from pathlib import Path
import sys
import threading
from turtle import setup
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot
from services import TinyDatabase, WebAccess
from playwright.sync_api import sync_playwright
from services import window, popup_window
import settings
from src.frontend import setup_tabs_and_tables
from src.shared import PointerLocation
from src.goto import late_alert
from src.autotel import batteries, long_rides

def setup_shared_resources(mode):
    return TinyDatabase({
        "autotel": ["autotelDB.json", "ride_id"],
        "goto": ["gotoDB.json", "ride_id"],
        "user": ["userDB.json", "username"],
    })
class WorkSignals(QObject):
    page_loaded = pyqtSignal(str, int, int, object)
    toast_signal = pyqtSignal(str, str, str)
    
    late_table_row = pyqtSignal(object)
    batteries_table_row = pyqtSignal(object)
    long_rides_table_row = pyqtSignal(object)
    
    request_phone_input = pyqtSignal()
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
        
        self.account = {}

    @pyqtSlot()
    def run(self):
        if data := self.db.find_one({'username': Path.home().name}, 'user'):
            self.account = data
        else:
            self.signals.request_phone_input.emit()
        with sync_playwright() as playwright:
            with WebAccess(playwright, settings.playwright_headless, 'Default') as web_access:
                web_access.create_pages({
                    "goto_bo": "https://car2gobo.gototech.co",
                    "autotel_bo": "https://prodautotelbo.gototech.co",
                    "pointer": "https://fleet.pointer4u.co.il/iservices/fleet2015/login"
                })
                if not self.account or not self.account.get('phone'):
                    self.stop_event.wait()
                    self.stop_event.clear()
                        
                self.signals.request_otp_input.emit()
                
                pointer = PointerLocation(web_access, self.account)
                
                self.stop_event.wait()
                self.stop_event.clear()
                
                pointer.fill_otp(self.account.get('code', ''))
                    
                if not self.running:
                    return

                
                late = late_alert.LateAlert(
                    self.db,
                    show_toast=lambda title, message, icon: self.signals.toast_signal.emit(title, message, icon),
                    gui_table_row=lambda row: self.signals.late_table_row.emit(row),
                    web_access=web_access,
                )
                batteries_alert = batteries.BatteriesAlert(
                    self.db,
                    show_toast=lambda title, message, icon: self.signals.toast_signal.emit(title, message, icon),
                    gui_table_row=lambda row: self.signals.batteries_table_row.emit(row),
                    web_access=web_access,
                    pointer=pointer,
                )
                
                long_rides_alert = long_rides.LongRides(
                    self.db,
                    show_toast=lambda title, message, icon: self.signals.toast_signal.emit(title, message, icon),
                    gui_table_row=lambda row: self.signals.long_rides_table_row.emit(row),
                    web_access=web_access,
                    pointer=pointer,
                )

                while self.running:
                    late.start_requests()
                    self.stop_event.wait(3)
                    long_rides_alert.start_requests()
                    batteries_alert.start_requests()
                    self.stop_event.wait(timeout=5 * 60)
                


    def set_account_data(self, data):
        for key, value in data.items():
            self.account[key] = value
        if 'phone' in data:
            self.db.upsert_one(
                {'username': self.account['username'], 'phone': self.account['phone']},
                'user'
            )

        self.stop_event.set()
        
    def stop(self):
        self.running = False
        self.stop_event.set()

def handle_phone_input(worker):
    username = Path.home().name
    cta = f"""
    <h2>Hey {username.replace('.', ' ').title()},</h2>
    <p>
    Welcome to your GOTO service companion!
    <br><br>
    Please enter your phone number to get started.
    </p>
    """
    popup = popup_window.PopupWindow(
        cta, message="Enter your phone here",
        icon=settings.app_icon, regex=r"^05\d{8}$"
    )
    phone_number = popup.get_input()
    worker.signals.input_received.emit({ "username": username, "phone": phone_number})
    

def handle_code_input(worker):
    cta = """
    <h2>We need to connect you to Pointer for location data</h2>
    <p>
    Please enter the code sent to your phone number.
    </p>
    """
    popup = popup_window.PopupWindow(
        cta, message="Enter your code here",
        icon=settings.app_icon, regex=r"^\d{6}$"
    )
    code = popup.get_input()
    worker.signals.input_received.emit({ "code": code })
    
if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        main_win = window.MainWindow(title="GotoGlobal", app_icon=settings.app_icon)
        
        db = setup_shared_resources(0)
    
        tables = setup_tabs_and_tables(main_win)

        worker = PlaywrightWorker(db)
        worker.signals.toast_signal.connect(main_win.show_toast)
        worker.signals.late_table_row.connect(tables['late_rides'].add_rows)
        worker.signals.batteries_table_row.connect(tables['batteries'].add_rows)
        worker.signals.long_rides_table_row.connect(tables['long_rides'].add_rows)
        worker.signals.request_phone_input.connect(lambda: handle_phone_input(worker))
        worker.signals.request_otp_input.connect(lambda: handle_code_input(worker))
        worker.signals.input_received.connect(worker.set_account_data)

        main_win.threadpool.start(worker)
        app.aboutToQuit.connect(worker.stop)

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
