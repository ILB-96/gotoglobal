import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from services import TinyDatabase, WebAccess
from playwright.sync_api import sync_playwright
import settings
from src.goto import late_alert


class TableTab(QWidget):
    def __init__(self, title):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.table = QTableWidget(10, 3)
        self.table.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3"])
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

    def update_table(self, row: int, col: int, text: str):
        self.table.setItem(row, col, QTableWidgetItem(text))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Goto Automation Dashboard")
        self.setGeometry(100, 100, 800, 400)

        self.tabs = QTabWidget()
        self.goto_tab = TableTab("Goto BO")
        self.autotel_tab = TableTab("Autotel BO")

        self.tabs.addTab(self.goto_tab, "Goto BO")
        self.tabs.addTab(self.autotel_tab, "Autotel BO")
        self.setCentralWidget(self.tabs)

        self.table_map = {
            "goto_bo": self.goto_tab,
            "autotel_bo": self.autotel_tab
        }

    def update_cell(self, tab_name, row, col, value):
        tab = self.table_map.get(tab_name)
        if tab:
            tab.update_table(row, col, value)


class PlaywrightWorker(QThread):
    page_loaded = pyqtSignal(str, int, int, str)

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.playwright = None
        self.web_access = None

    def run(self):
        with sync_playwright() as playwright:
            self.playwright = playwright
            with WebAccess(playwright, settings.playwright_headless, "Default") as web_access:
                self.web_access = web_access
                web_access.start_context("")
                web_access.create_pages({
                    "goto_bo": "https://car2gobo.gototech.co",
                    "autotel_bo": "https://prodautotelbo.gototech.co"
                })

                self.page_loaded.emit("goto_bo", 0, 0, "Page Loaded")
                self.page_loaded.emit("autotel_bo", 0, 0, "Page Loaded")

                # Start alert logic, block here until it finishes
                late_alert.LateAlert(self.db).start_requests(web_access)

                # Keep thread alive until GUI closes
                self.exec()

    def cleanup(self):
        self.quit()
        self.wait()


def setup_shared_resources(mode):
    return TinyDatabase({
        "autotel": ["autotelDB.json", "ride_id"],
        "goto": ["gotoDB.json", "ride_id"]
    })


if __name__ == "__main__":
    db = setup_shared_resources(0)
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()

    # Start Playwright thread
    worker = PlaywrightWorker(db)
    worker.page_loaded.connect(main_win.update_cell)
    worker.start()

    # Ensure cleanup when app exits
    def on_exit():
        worker.cleanup()

    app.aboutToQuit.connect(on_exit)
    sys.exit(app.exec())
