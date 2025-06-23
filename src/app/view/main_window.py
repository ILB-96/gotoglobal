# coding: utf-8
import threading
from PyQt6.QtCore import Qt, pyqtSignal, QEasingCurve, QUrl, QSize, QTimer
from PyQt6.QtGui import QIcon, QDesktopServices, QColor
from PyQt6.QtWidgets import QApplication

from services.fluent.qfluentwidgets import (FluentWindow,
                            SplashScreen, SystemThemeListener, isDarkTheme, NavigationItemPosition)
import settings
from src.shared import utils
from ..common.config import cfg

from .goto_interface import GotoInterface
from .autotel_interface import AutotelInterface

from win11toast import toast

class MainWindow(FluentWindow):

    def __init__(self, title,app_icon):
        super().__init__()
        self.initWindow(title, app_icon)

        # create system theme listener
        self.themeListener = SystemThemeListener(self)

        self.gotoInterface = GotoInterface(self)
        self.autotelInterface = AutotelInterface(self)
        self.navigationInterface.setAcrylicEnabled(True)

        pos = NavigationItemPosition.SCROLL
        self.addSubInterface(self.gotoInterface, QIcon(utils.resource_path(settings.app_icon)), "Goto", pos)
        self.addSubInterface(self.autotelInterface, QIcon(utils.resource_path(settings.autotel_icon)), "Autotel", pos)
        # self.navigationInterface.hide()


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
    def __remove(self, widget):
        if widget is not None:
            self.navigationInterface.removeWidget(widget)
            widget.setParent(None)
            widget.deleteLater()
    def removeWidgets(self):
        self.gotoInterface.removeWidgets()
        self.autotelInterface.removeWidgets()
        if not cfg.get(cfg.long_rides) and not cfg.get(cfg.batteries):
            self.__remove(self.autotelInterface)
        if not cfg.get(cfg.late_rides):
            self.__remove(self.gotoInterface)

        if (not cfg.get(cfg.long_rides) and not cfg.get(cfg.batteries)) or not cfg.get(cfg.late_rides):
            self.navigationInterface.hide()
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
    