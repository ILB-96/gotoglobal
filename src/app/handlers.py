
from .view.settings_interface import SettingsPopup

from PyQt6.QtWidgets import QVBoxLayout, QLineEdit
from PyQt6.QtCore import pyqtSignal, Qt
from services.fluent.qfluentwidgets import PrimaryPushButton, InfoBar, FluentStyleSheet, BodyLabel

from qframelesswindow import FramelessDialog

from PyQt6.QtWidgets import QVBoxLayout, QLineEdit
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from qframelesswindow import FramelessDialog


class CodeInputDialog(FramelessDialog):
    codeEntered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setWindowTitle("Pointer Login")
        self.setResizeEnabled(False)
        self.resize(420, 200)
        self.titleBar.hide()
        FluentStyleSheet.DIALOG.apply(self)

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # --- CTA section ---
        self.ctaLabel = BodyLabel(
            "🔐 <b>We need to connect you to Pointer for location data</b><br><br>"
            "Please enter the code sent to your phone number."
        )
        self.ctaLabel.setWordWrap(True)
        self.ctaLabel.setTextFormat(Qt.TextFormat.RichText)
        self.layout.addWidget(self.ctaLabel)

        # --- Code input ---
        self.codeInput = QLineEdit(self)
        self.codeInput.setPlaceholderText("Enter 6-digit code")
        self.codeInput.setMaxLength(6)
        self.codeInput.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.codeInput.setFixedHeight(36)
        self.layout.addWidget(self.codeInput)

        # --- Submit button ---
        self.submitBtn = PrimaryPushButton("Submit", self)
        self.submitBtn.clicked.connect(self.handle_submit)
        self.layout.addWidget(self.submitBtn)

    def handle_submit(self):
        code = self.codeInput.text()
        if code.isdigit() and len(code) == 6:
            self.codeEntered.emit(code)
            self.accept()
        else:
            QTimer.singleShot(0, lambda: InfoBar.error(
                "Invalid Code",
                "Please enter a valid 6-digit code.",
                parent=self  # or self.parent() if dialog hasn't been shown yet
            ))
    def get_code(self):
        if self.exec() == self.DialogCode.Accepted:
            return self.codeInput.text()
        return None


def handle_settings_input():
    dialog = SettingsPopup()
    dialog.exec()

def handle_code_input(worker):
    dialog = CodeInputDialog()
    code = dialog.get_code()
    if code:
        worker.input_received.emit({"code": code})


def handle_start_loading(tables):
    for table in tables.values():
        try:
            table.start_loading()
        except Exception:
            pass

def handle_stop_loading(tables):
    for table in tables.values():
        try:
            table.stop_loading()
        except Exception:
            pass