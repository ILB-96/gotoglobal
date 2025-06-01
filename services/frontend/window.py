import time

from PyQt6.QtCore import (
    QTimer,
    QThreadPool,
)
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTabWidget,
    QTableWidget,
)
from PyQt6.QtGui import QIcon
from win11toast import toast

class MainWindow(QMainWindow):
    def __init__(self, title, app_icon, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setGeometry(100, 100, 800, 400)
        self.setWindowIcon(QIcon(app_icon))
        self.tabs = QTabWidget()
        self.setWindowTitle(title)
        self.threadpool = QThreadPool()

        self.setCentralWidget(self.tabs)
        
    def build_tab(self, title: str, widgets: list[QWidget]):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        tab.setObjectName(title.lower().replace(' ', '_'))
        for widget in widgets:
            layout.addWidget(widget)
        self.tabs.addTab(tab, title)
        return tab

    def show_toast(self, title, msg, icon):        
        toast(
            title,
            msg,
            button="Dismiss",
            icon=icon)
        
    def run_task(self, task):
        task()