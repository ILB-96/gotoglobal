from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIcon
import re

class PopupWindow(QDialog):
    confirmed = pyqtSignal(str)

    def __init__(self, cta, title="Authorization", message="Please enter a value:", icon=None, parent=None, regex=None, regex_error="Invalid format."):
        super().__init__(parent)
        self.setModal(True)
        self.input_value = None
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 500, 250)
        self.regex = re.compile(regex) if regex else None
        self.regex_error = regex_error
        if icon:
            self.setWindowIcon(QIcon(icon))

        # Widgets
        self.label = QLabel(cta)
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText(message)
        self.confirm_button = QPushButton("Confirm")
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-size: 10pt;")
        self.error_label.setVisible(False)

        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
                font-family: 'Tahoma', 'Arial';
            }
            QLabel {
                font-size: 14pt;
                color: #333;
            }
            QLineEdit {
                font-size: 14pt;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-bottom: 16px;
                margin-top: 16px;
            }
            QPushButton {
                font-size: 14pt;
                padding: 8px 20px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

        # Layout
        input_button_layout = QHBoxLayout()
        input_button_layout.addWidget(self.line_edit)
        input_button_layout.addWidget(self.confirm_button)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addLayout(input_button_layout)
        layout.addWidget(self.error_label)
        self.setLayout(layout)

        # Signals
        self.confirm_button.clicked.connect(self.on_confirm)

    def on_confirm(self):
        value = self.line_edit.text().strip()
        if not value:
            self.error_label.setText("Input is required.")
            self.error_label.setVisible(True)
            return
        if self.regex and not self.regex.fullmatch(value):
            self.error_label.setText(self.regex_error)
            self.error_label.setVisible(True)
            return
        self.error_label.setVisible(False)
        self.input_value = value
        self.confirmed.emit(self.input_value)
        self.accept()

    def get_input(self):
        result = self.exec()
        return self.input_value if result == QDialog.DialogCode.Accepted else None