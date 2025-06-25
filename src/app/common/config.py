# coding:utf-8
from pathlib import Path
import sys
from enum import Enum

from PyQt6.QtCore import QLocale
from services.fluent.qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            OptionsValidator, RangeConfigItem, RangeValidator,
                            FolderListValidator, Theme, FolderValidator, ConfigSerializer, ConfigValidator, __version__)

def isWin11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000


class Config(QConfig):
    """ Config of application """

    # main window
    late_rides = ConfigItem("MainWindow", "lateRidesEnabled", True, BoolValidator())
    long_rides = ConfigItem("MainWindow", "longRidesEnabled", True, BoolValidator())
    batteries = ConfigItem("MainWindow", "batteriesEnabled", True, BoolValidator())
    create_whatsapp_page = ConfigItem("MainWindow", "whatsappEnabled", True, BoolValidator())
    pointer = ConfigItem("MainWindow", "pointerEnabled", True, BoolValidator())
    pointer_user = ConfigItem("MainWindow", "pointerUsername", Path.home().name, ConfigValidator())
    phone = ConfigItem("MainWindow", "phoneNumber", "", ConfigValidator())
    create_goto_tabs = ConfigItem("MainWindow", "createGotoTabs", True, BoolValidator())
    create_autotel_tabs = ConfigItem("MainWindow", "createAutotelTabs", True, BoolValidator())

    # software update
    checkUpdateAtStartUp = ConfigItem("Update", "CheckUpdateAtStartUp", True, BoolValidator())


YEAR = 2025
AUTHOR = "Israel Barmack"
VERSION = __version__
FEEDBACK_URL = "https://github.com/ILB-96/gotoglobal/issues"


cfg = Config()
cfg.themeMode.value = Theme.AUTO
qconfig.load('app/config/config.json', cfg)