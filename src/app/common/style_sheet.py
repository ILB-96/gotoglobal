# coding: utf-8
from enum import Enum

from services.fluent.qfluentwidgets import StyleSheetBase, Theme, isDarkTheme, qconfig
from src.shared import utils


class StyleSheet(StyleSheetBase, Enum):
    """ Style sheet  """

    LINK_CARD = "link_card"
    SAMPLE_CARD = "sample_card"
    HOME_INTERFACE = "home_interface"
    ICON_INTERFACE = "icon_interface"
    VIEW_INTERFACE = "view_interface"
    SETTING_INTERFACE = "setting_interface"
    GALLERY_INTERFACE = "gallery_interface"
    NAVIGATION_VIEW_INTERFACE = "navigation_view_interface"

    def path(self, theme=Theme.AUTO):
        theme = qconfig.theme if theme == Theme.AUTO else theme
        return utils.resource_path(f"src/app/resource/qss/{theme.value.lower()}/{self.value}.qss")
