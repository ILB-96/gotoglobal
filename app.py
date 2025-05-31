import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from services import TinyDatabase, WebAccess
from playwright.sync_api import sync_playwright
from services import window, table
import settings
from src.goto import late_alert


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
    goto_late_rides.start_loading_indicator()
    main_win.build_tab(title="Goto", widgets=[goto_late_rides])
    return goto_late_rides


def autotel_tab(main_win):
    batteries_table = table.Table(
        title="Autotel Batteries",
        columns=["Ride ID", "License Plate", "Battery", "Location"],
    )
    batteries_table.start_loading_indicator()
    main_win.build_tab(title="Autotel", widgets=[batteries_table])
    return batteries_table


class PlaywrightWorker(QThread):
    page_loaded = pyqtSignal(str, int, int, str)
    toast_signal = pyqtSignal(str, str, str)

    def __init__(self, db, late_rides_table, batteries_table):
        super().__init__()
        self.db = db
        self.late = None
        self.late_rides_table = late_rides_table
        self.timer = QTimer()  # Create here but configure later

    def run(self):
        # Timer must be moved to this thread
        self.timer.moveToThread(self)

        with sync_playwright() as playwright:
            with WebAccess(playwright, settings.playwright_headless, "Default") as web_access:
                web_access.start_context("")
                web_access.create_pages({
                    "goto_bo": "https://car2gobo.gototech.co",
                    "autotel_bo": "https://prodautotelbo.gototech.co"
                })

                self.page_loaded.emit("goto_bo", 0, 0, "Page Loaded")
                self.page_loaded.emit("autotel_bo", 0, 0, "Page Loaded")

                self.late = late_alert.LateAlert(
                    self.db,
                    show_toast=lambda title, msg, icon: self.toast_signal.emit(title, msg, icon),
                    gui_table=self.late_rides_table,
                    web_access=web_access,
                )

                # Initial load
                self.late.start_requests()
                self.late_rides_table.stop_loading_indicator()

                # Setup timer in the correct thread after everything is initialized
                self.timer.setInterval(15 * 60 * 1000)
                self.timer.timeout.connect(self.late.start_requests)
                self.timer.start()

                self.exec()  # Start thread event loop

    def cleanup(self):
        if self.timer and self.timer.isActive():
            self.timer.stop()
        self.quit()
        self.wait()


if __name__ == "__main__":
    db = setup_shared_resources(0)
    app = QApplication(sys.argv)
    main_win = window.MainWindow(title="GotoGlobal", app_icon=settings.app_icon)

    late_rides_table = goto_tab(main_win)
    batteries_table = autotel_tab(main_win)

    worker = PlaywrightWorker(db, late_rides_table, batteries_table)
    worker.toast_signal.connect(main_win.show_toast)
    worker.start()

    main_win.show()
    sys.exit(app.exec())
