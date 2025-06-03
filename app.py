from pathlib import Path
import sys
import threading
from time import sleep
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QRunnable, QObject, pyqtSignal, pyqtSlot, QTimer
from services import TinyDatabase, WebAccess
from playwright.sync_api import sync_playwright
from services import window, table, popup_window
import settings
from src.goto import late_alert
from src.autotel import batteries

def setup_shared_resources(mode):
    return TinyDatabase({
        "autotel": ["autotelDB.json", "ride_id"],
        "goto": ["gotoDB.json", "ride_id"]
    })


def goto_tab(main_win):
    goto_late_rides = table.Table(
        title="Late Rides",
        columns=["Ride ID", "End Time", "Future Ride", "Future Ride Time"]
    )
    main_win.build_tab(title="Goto", widgets=[goto_late_rides])
    return goto_late_rides


def autotel_tab(main_win):
    batteries_table = table.Table(
        title="Autotel Batteries",
        columns=["Ride ID", "License Plate", "Battery", "Location"],
    )
    main_win.build_tab(title="Autotel", widgets=[batteries_table])
    return batteries_table

class WorkSignals(QObject):
    page_loaded = pyqtSignal(str, int, int, object)
    toast_signal = pyqtSignal(str, str, str)
    late_table_row = pyqtSignal(object)
    batteries_table_row = pyqtSignal(object)
    gui_table_update = pyqtSignal(str)
    
    start_loading = pyqtSignal()
    stop_loading = pyqtSignal()
class PlaywrightWorker(QRunnable):

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.signals = WorkSignals()
        self.running = True
        self.stop_event = threading.Event()

    @pyqtSlot()
    def run(self):
        playwright = sync_playwright().start()
        web_access = WebAccess(playwright, settings.playwright_headless, 'Default')
        web_access.create_pages({
            "goto_bo": "https://car2gobo.gototech.co",
            "autotel_bo": "https://prodautotelbo.gototech.co",
            "pointer": "https://fleet.pointer4u.co.il/iservices/fleet2015/login"
        })

        late = late_alert.LateAlert(
            self.db,
            show_toast=lambda *args, **kwargs: self.signals.toast_signal.emit(*args, **kwargs),
            gui_table_row=lambda row: self.signals.late_table_row.emit(row),
            web_access=web_access,
        )
        batteries_alert = batteries.BatteriesAlert(
            self.db,
            show_toast=lambda *args, **kwargs: self.signals.toast_signal.emit(*args, **kwargs),
            gui_table_row=lambda row: self.signals.batteries_table_row.emit(row),
            web_access=web_access
        )
        
        
        # self.signals.page_loaded.emit("goto_bo", 0, 0, )
        # self.signals.page_loaded.emit("autotel_bo", 0, 0, )
        while self.running:
            late.start_requests()
            for _ in range(3):
                if self.stop_event.is_set():
                    break
                batteries_alert.start_requests()
                self.stop_event.wait(timeout=5 * 60)

        
    def stop(self):
        self.running = False
        self.stop_event.set()


if __name__ == "__main__":
    db = setup_shared_resources(0)

    app = QApplication(sys.argv)
    main_win = window.MainWindow(title="GotoGlobal", app_icon=settings.app_icon)

    late_rides_table = goto_tab(main_win)
    batteries_table = autotel_tab(main_win)
    username = Path.home().name.replace('.', ' ').title()
    cta = f"""
    <h2>Hey {username},</h2>
    <p>
    welcome to your Goto service companion!
    <br>
    <br>
    This app helps you monitor rides in real-time.
    <br>
    Please enter your phone number to get started.
    </p>
    """

    popup = popup_window.PopupWindow(cta, message="Enter your phone here")
    phone_number = popup.get_input()
    # worker = PlaywrightWorker(db)
    # worker.signals.toast_signal.connect(main_win.show_toast)
    # worker.signals.late_table_row.connect(late_rides_table.add_rows)
    # worker.signals.batteries_table_row.connect(batteries_table.add_rows)

    # main_win.threadpool.start(worker)
    # app.aboutToQuit.connect(worker.stop)
    late_rides_table.add_rows([
        ["12345", "2023-10-01 12:00", "No", "N/A"],
        ["67890", "2023-10-01 14:30", "Yes", "2023-10-01 15:00"]
    ])
    main_win.show()
    sys.exit(app.exec())
