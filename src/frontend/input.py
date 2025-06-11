import re
from PyQt6.QtWidgets import QLineEdit

class Input(QLineEdit):
    def __init__(self, parent=None, title="data", placeholder="Enter text here...", validator=r"^\d{6}$",
        error_message="Code must be 6 digits"):
        super().__init__(parent)
        self.title = title
        self.setPlaceholderText(placeholder)
        self.setStyleSheet("QLineEdit { font-size: 14px; font-family: 'Tahoma', 'Arial'; padding: 8px; border-radius: 4px; }")

    def is_valid(self):
        return bool(re.fullmatch(r"^\d{6}$", self.text().strip()))
        
        
    def get_data(self):
        return {self.title: self.text().strip()}