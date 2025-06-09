from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon
import re

class PopupWindow(QDialog):
    confirmed = pyqtSignal(str)

    def __init__(self, cta, title="Authorization", icon=None, parent=None, widgets=None):
        super().__init__(parent)
        self.setModal(True)
        self.input_value = None
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 500, 250)
        if icon:
            self.setWindowIcon(QIcon(icon))

        # Widgets
        self.label = QLabel(cta)
        self.confirm_button = QPushButton("Confirm")
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-size: 10pt;")
        self.error_label.setVisible(False)
        self.widgets = widgets or []
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
        input_button_layout.addWidget(self.confirm_button)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addLayout(input_button_layout)
        self.layout.addWidget(self.error_label)
        
        for widget in self.widgets:
            self.layout.addWidget(widget)
        self.setLayout(self.layout)

        # Signals
        self.confirm_button.clicked.connect(self.on_confirm)

    def on_confirm(self):
        if not self.widgets:
            self.error_label.setText("Missing widgets.")
            self.error_label.setVisible(True)
            return
        
        

        self.error_label.setVisible(False)
        self.confirmed.emit(self.input_value)
        self.accept()

    def get_input(self):
        result = self.exec()
        data = {}
        for widget in self.widgets:
            widget_data = widget.get_data() if hasattr(widget, 'get_data') else None
            if widget_data:
                data.update(widget_data)
            
        return data if result == QDialog.DialogCode.Accepted else None