import threading
from PyQt6.QtCore import Qt
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
        self.update_tabs_style()
       

        self.setCentralWidget(self.tabs)

    def build_tab(self, title: str, color: str, widgets: list[QWidget]):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        tab.setObjectName(title)
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
    
    def delete_tab(self, object_name: str):
        index = self.tabs.indexOf(self.tabs.findChild(QWidget, object_name))
        if index != -1:
            self.tabs.removeTab(index)
            return True
        return False
    
    def delete_table_from_tab(self, tab_object_name: str, table_object_name: str):
        tab = self.tabs.findChild(QWidget, tab_object_name)
        if not tab:
            return
        
        table = tab.findChild(QWidget, table_object_name)
        if not table:
            return
        
        layout = tab.layout()
        if layout:
            layout.removeWidget(table)
            table.deleteLater()
