# coding: utf-8
import threading
from PyQt6.QtCore import Qt, pyqtSignal, QEasingCurve, QUrl, QSize, QTimer
from PyQt6.QtGui import QIcon, QDesktopServices, QColor
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QFrame, QWidget

from services.fluent.qfluentwidgets import (FluentWindow,
                            SplashScreen, SystemThemeListener, isDarkTheme)

from .gallery_interface import GalleryInterface

from .view_interface import ViewInterface

from ..common.icon import Icon
from win11toast import toast

class MainWindow(FluentWindow):

    def __init__(self, title,app_icon):
        super().__init__()
        self.initWindow(title, app_icon)

        # create system theme listener
        self.themeListener = SystemThemeListener(self)

        self.viewInterface = ViewInterface(self)
        self.addSubInterface(self.viewInterface, Icon.GRID, "")
        self.navigationInterface.hide()


        self.splashScreen.finish()

        # start theme listener
        self.themeListener.start()


    def initWindow(self, title, app_icon):
        self.resize(960, 780)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon(app_icon))
        self.setWindowTitle(title)

        self.setMicaEffectEnabled(True)

        # create splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(106, 106))
        self.splashScreen.raise_()

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        self.show()
        QApplication.processEvents()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())

    def closeEvent(self, e):
        self.themeListener.terminate()
        self.themeListener.deleteLater()
        super().closeEvent(e)

    def _onThemeChangedFinished(self):
        super()._onThemeChangedFinished()

        # retry
        if self.isMicaEffectEnabled():
            QTimer.singleShot(100, lambda: self.windowEffect.setMicaEffect(self.winId(), isDarkTheme()))
            
    def show_toast(self, title, message, icon=None, duration='short'):
        def _run_toast():
            toast(title, message, icon=icon, duration=duration)

        threading.Thread(target=_run_toast, daemon=True).start()
    