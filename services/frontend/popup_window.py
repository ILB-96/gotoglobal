from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtCore import pyqtSignal, Qt
class PopupWindow(QDialog):
    confirmed = pyqtSignal(str)  # Optional: emits input if you want to connect it outside

    def __init__(self, cta, title="Authorization", message="Please enter a value:", parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.input_value = None  # The stored value
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 500, 250)

        # Widgets
        self.label = QLabel(cta)
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText(message)
        self.confirm_button = QPushButton("Confirm")
        
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

        self.setLayout(layout)

        # Signals
        self.confirm_button.clicked.connect(self.on_confirm)

    def on_confirm(self):
        self.input_value = self.line_edit.text()
        self.confirmed.emit(self.input_value)  # Optional
        self.accept()

    def get_input(self):
        result = self.exec()  # Shows the popup
        return self.input_value if result == QDialog.DialogCode.Accepted else None