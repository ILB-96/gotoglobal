import time

from PyQt6.QtCore import (
    QThreadPool,
    QPropertyAnimation, 
    QEasingCurve,
    Qt,
    QPoint
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
    QStyleFactory,
    QGraphicsOpacityEffect,
    QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QIcon, QFont, QColor
from win11toast import toast

class MainWindow(QMainWindow):
    def __init__(self, title, app_icon, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowIcon(QIcon(app_icon))
        self.tabs = QTabWidget()
        self.setWindowTitle(title)
        self.threadpool = QThreadPool()
        
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
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                font-weight: bold;
                color: #0055aa;
            }
            QTabBar::tab:hover {
                background: #d0d0d0;
            }
            
        """)

        self.setCentralWidget(self.tabs)


        
    def build_tab(self, title: str, widgets: list[QWidget]):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        tab.setObjectName(title.lower().replace(' ', '_'))
        for widget in widgets:
            layout.addWidget(widget)
        self.tabs.addTab(tab, title)
        return tab

    def show_toast(self, title, message, icon=None):
        toast(title, message, icon=icon)
        
    def fade_in_window(self):
        self.setWindowOpacity(0)
        animation = QPropertyAnimation(self, b"windowOpacity")
        animation.setDuration(600)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        animation.start()
        self._animation = animation
