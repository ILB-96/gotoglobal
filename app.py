import sys
from time import sleep
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QRunnable, QObject, pyqtSignal, pyqtSlot, QTimer
from services import TinyDatabase, WebAccess
from playwright.sync_api import sync_playwright
from services import window, table
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
    late_table_row = pyqtSignal(tuple)
    batteries_table_row = pyqtSignal(tuple)
    
    start_loading = pyqtSignal()
    stop_loading = pyqtSignal()
class PlaywrightWorker(QRunnable):

    def __init__(self, db, web_access):
        super().__init__()
        self.db = db
        self.web_access = web_access
        self.signals = WorkSignals()

    @pyqtSlot()
    def run(self):

        web_access.create_pages({
            "goto_bo": "https://car2gobo.gototech.co",
            "autotel_bo": "https://prodautotelbo.gototech.co",
            "pointer": "https://fleet.pointer4u.co.il/iservices/fleet2015/login"
        })

        late = late_alert.LateAlert(
            self.db,
            show_toast=lambda title, msg, icon: self.signals.toast_signal.emit(title, msg, icon),
            gui_table_row=lambda row: self.signals.late_table_row.emit(row),
            web_access=self.web_access,
        )
        batteries_alert = batteries.BatteriesAlert(self.db,
            show_toast=lambda title, msg, icon: self.signals.toast_signal.emit(title, msg, icon),
            gui_table_row=lambda row: self.signals.batteries_table_row.emit(row),
            web_access=self.web_access)
        late.start_requests()
        batteries_alert.start_requests()
        
        # self.signals.page_loaded.emit("goto_bo", 0, 0, )
        # self.signals.page_loaded.emit("autotel_bo", 0, 0, )




    def cleanup(self):
        self.quit()
        self.wait()


if __name__ == "__main__":
    db = setup_shared_resources(0)
    with sync_playwright() as playwright:
        with WebAccess(playwright, settings.playwright_headless, "Default") as web_access:
            app = QApplication(sys.argv)
            main_win = window.MainWindow(title="GotoGlobal", app_icon=settings.app_icon)

            late_rides_table = goto_tab(main_win)
            batteries_table = autotel_tab(main_win)

            worker = PlaywrightWorker(db, web_access)
            worker.toast_signal.connect(main_win.show_toast)
            worker.page_loaded.connect(main_win.run_task)
            worker.late_table_row.connect(late_rides_table.add_row)
            worker.batteries_table_row.connect(batteries_table.add_row)
            
            main_win.threadpool.start(worker)


            main_win.show()
            sys.exit(app.exec())
