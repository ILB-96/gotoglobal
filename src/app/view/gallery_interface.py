# coding:utf-8
from PyQt6.QtCore import Qt, pyqtSignal, QUrl, QEvent
from PyQt6.QtGui import QDesktopServices, QPainter, QPen, QColor
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame

from services.fluent.qfluentwidgets import (ScrollArea, PushButton, ToolButton, FluentIcon,
                            isDarkTheme, IconWidget, Theme, ToolTipFilter, TitleLabel, CaptionLabel,
                            StrongBodyLabel, BodyLabel, toggleTheme)
from ..common.config import FEEDBACK_URL
from ..common.icon import Icon
from ..common.style_sheet import StyleSheet
from ..common.signal_bus import signalBus


class SeparatorWidget(QWidget):
    """ Seperator widget """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedSize(6, 16)

    def paintEvent(self, e):
        painter = QPainter(self)
        pen = QPen(1)
        pen.setCosmetic(True)
        c = QColor(255, 255, 255, 21) if isDarkTheme() else QColor(0, 0, 0, 15)
        pen.setColor(c)
        painter.setPen(pen)

        x = self.width() // 2
        painter.drawLine(x, 0, x, self.height())


class ToolBar(QWidget):
    """ Tool bar """

    def __init__(self, title, subtitle, parent=None):
        super().__init__(parent=parent)
        # self.subtitleLabel = CaptionLabel(subtitle, self)

        self.themeButton = ToolButton(FluentIcon.CONSTRACT, self)
        self.separator = SeparatorWidget(self)
        self.feedbackButton = ToolButton(FluentIcon.FEEDBACK, self)

        self.vBoxLayout = QVBoxLayout(self)
        self.buttonLayout = QHBoxLayout()

        self.__initWidget()

    def __initWidget(self):
        self.setFixedHeight(70)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(36, 0, 36, 0)
        self.vBoxLayout.addSpacing(4)
        self.vBoxLayout.addLayout(self.buttonLayout, 1)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.buttonLayout.setSpacing(4)
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonLayout.addStretch(1)
        self.buttonLayout.addWidget(self.themeButton, 0, Qt.AlignmentFlag.AlignRight)
        self.buttonLayout.addWidget(self.separator, 0, Qt.AlignmentFlag.AlignRight)
        self.buttonLayout.addWidget(self.feedbackButton, 0, Qt.AlignmentFlag.AlignRight)
        self.buttonLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        self.themeButton.installEventFilter(ToolTipFilter(self.themeButton))        
        self.feedbackButton.installEventFilter(
            ToolTipFilter(self.feedbackButton))
        self.themeButton.setToolTip(self.tr('Toggle theme'))
        self.feedbackButton.setToolTip(self.tr('Send feedback'))

        self.themeButton.clicked.connect(lambda: toggleTheme(True))
        self.feedbackButton.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL)))

class GalleryInterface(ScrollArea):
    """ Gallery interface """

    def __init__(self, title: str, subtitle: str, parent=None):
        """
        Parameters
        ----------
        title: str
            The title of gallery

        subtitle: str
            The subtitle of gallery

        parent: QWidget
            parent widget
        """
        super().__init__(parent=parent)
        self.view = QWidget(self)
        self.toolBar = ToolBar(title, subtitle, self)
        self.vBoxLayout = QVBoxLayout(self.view)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, self.toolBar.height(), 0, 0)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.vBoxLayout.setSpacing(8)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.setContentsMargins(36, 0, 36, 36)
        # self.vBoxLayout.addWidget(self.toolBar, 0, Qt.AlignmentFlag.AlignTop)
        self.view.setObjectName('view')
        StyleSheet.GALLERY_INTERFACE.apply(self)

    def scrollToCard(self, index: int):
        """ scroll to example card """
        w = self.vBoxLayout.itemAt(index).widget()
        self.verticalScrollBar().setValue(w.y())

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.toolBar.resize(self.width(), self.toolBar.height())
