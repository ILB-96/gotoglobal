from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtCore import Qt
from services.fluent.qfluentwidgets import PrimaryPushButton, FluentStyleSheet, BodyLabel

from qframelesswindow import FramelessDialog

from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtCore import Qt
from qframelesswindow import FramelessDialog


class PointerInputInterface(FramelessDialog):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setWindowTitle("Pointer Login")
        self.setResizeEnabled(False)
        self.resize(320, 200)
        self.titleBar.hide()
        FluentStyleSheet.DIALOG.apply(self)

        self.mainLayout = QVBoxLayout(self)
        self.setLayout(self.mainLayout)

        self.ctaLabel = BodyLabel(
            "🔐 <b>We need to connect you to Pointer for location data</b><br><br>"
            "Please enter the code sent to your phone number."
        )
        self.ctaLabel.setWordWrap(True)
        self.ctaLabel.setTextFormat(Qt.TextFormat.RichText)
        self.mainLayout.addWidget(self.ctaLabel)

        self.submitBtn = PrimaryPushButton("I'm in", self)
        self.submitBtn.clicked.connect(self.accept)
        self.mainLayout.addWidget(self.submitBtn)