import time

from PyQt6.QtCore import (
    QTimer,
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

class MainWindow(QMainWindow):
    def __init__(self, title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setGeometry(100, 100, 800, 400)
        
        self.tabs = QTabWidget()
        self.setWindowTitle(title)
        
        
        self.setCentralWidget(self.tabs)
        
    def build_tab(self, title: str, widgets: list[QWidget]):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        for widget in widgets:
            layout.addWidget(widget)
        self.tabs.addTab(tab, title)
        return tab