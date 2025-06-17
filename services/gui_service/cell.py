from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt
from typing import Callable, Optional


class Cell(QWidget):
    def __init__(self, content: str):
        super().__init__()
        self.content = content
        layout = QHBoxLayout(self)
        label = QLabel(self.content)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)


class ButtonCell(QWidget):
    def __init__(self, content: str, callback: Optional[Callable] = None, btn_colors=("#4caf50", '#45a049', '#388e3c')):
        super().__init__()
        self.content = content
        self.callback = callback

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        button = QPushButton(self.content)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(f"""
            QPushButton {{
                min-height: 24px;
                padding: 6px 14px;
                background-color: {btn_colors[0]};
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 15px;
                font-weight: 700;
                font-family: 'Tahoma', 'Arial';
            }}
            QPushButton:hover {{
                background-color: {btn_colors[1]};
            }}
            QPushButton:pressed {{
                background-color: {btn_colors[2]};
            }}
        """)
        if self.callback:
            button.clicked.connect(self.callback)

        layout.addWidget(button)
