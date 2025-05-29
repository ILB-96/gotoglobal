import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

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


if __name__ == "__main__":
    db = setup_shared_resources(0)
    app = QApplication(sys.argv)
    main_win = window.MainWindow(title="GotoGlobal")
    late_table = table.Table(
        name="Late Rides",
        columns=["Ride ID", "End Time", "Future Ride", "Future Ride Time"],
    )
    batteries_table = table.Table(
        name="Autotel Batteries",
        columns=["Ride ID", "License Plate", "Battery", "Location"],
    )
    main_win.build_tab(
        title="Goto",
        widgets=[
            late_table]
    )
    main_win.build_tab(
        title="Autotel",
        widgets=[
            batteries_table]
    )
    main_win.show()

    sys.exit(app.exec())
