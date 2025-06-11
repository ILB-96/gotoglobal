import threading
from PyQt6.QtCore import (
    QThreadPool,
    Qt,
)
from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QTabWidget,
)
from PyQt6.QtGui import QIcon, QColor
from win11toast import toast

class MainWindow(QMainWindow):
    def __init__(self, title, app_icon, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setGeometry(100, 100, 1000, 800)
        self.setWindowIcon(QIcon(app_icon))
        self.tabs = QTabWidget()
        self.setWindowTitle(title)
        self.threadpool = QThreadPool()
        self.update_tabs_style()
       

        self.setCentralWidget(self.tabs)

    def build_tab(self, title: str, color: str, widgets: list[QWidget]):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        for widget in widgets:
            layout.addWidget(widget)
        tab.setCursor(Qt.CursorShape.PointingHandCursor)

        self.tabs.addTab(tab, title)

        index = self.tabs.indexOf(tab)
        tab_bar = self.tabs.tabBar()
        tab_bar is not None and tab_bar.setTabTextColor(index, QColor(color)) # type: ignore

        return tab

    def update_tabs_style(self):
        # Global style for appearance (not color)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                background: #fff;
                border: none;
                font-size: 16pt;
                font-family: 'Tahoma', 'Arial';
            }
            QTabBar::tab {
                background: #e0e0e0;
                padding: 6px 12px;
                margin-right: 4px;
                font-size: 12pt;
                min-width: 120px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background: #d0d0d0;
            }
        """)

    def show_toast(self, title, message, icon=None, duration='short'):
        def _run_toast():
            toast(title, message, icon=icon, duration=duration)

        threading.Thread(target=_run_toast, daemon=True).start()