from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel, QLineEdit, QGroupBox,
    QGraphicsDropShadowEffect, QStyleOptionButton
)
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QPaintEvent

from src.shared import User



class PaintedCheckBox(QCheckBox):
    def __init__(self, label="", parent=None):
        super().__init__(label, parent)
        self.setMouseTracking(True)
        self._hover = False

    def enterEvent(self, event):
        self._hover = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event: QPaintEvent):
        super().paintEvent(event)
        self.setStyleSheet("margin-left: 2px;")  # Keeps text aligned with box

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.style().subElementRect(
            self.style().SubElement.SE_CheckBoxIndicator,
            self.styleOption(),
            self,
        )

        if self.isChecked():
            # Checked style
            painter.setBrush(QColor("#0078D4"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect, 4, 4)

            # Draw checkmark
            painter.setPen(QPen(Qt.GlobalColor.white, 2.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            path = [
                QPointF(rect.left() + rect.width() * 0.25, rect.center().y()),
                QPointF(rect.center().x() - 2, rect.bottom() - rect.height() * 0.3),
                QPointF(rect.right() - rect.width() * 0.2, rect.top() + rect.height() * 0.3),
            ]
            painter.drawPolyline(path)
        else:
            if self._hover:
                painter.setBrush(QColor("#CEE8FC"))  # Soft blue hover background
            else:
                painter.setBrush(QColor("#f8f8f8"))  # Light neutral

            painter.setPen(QPen(QColor("#c6c6c6"), 1.2))
            painter.drawRoundedRect(rect, 4, 4)

    def styleOption(self):
        option = QStyleOptionButton()
        self.initStyleOption(option)
        return option
    
class SettingsPanel(QWidget):
    def __init__(self, account: User, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #fefcfd;")
        self.error_message = "Please fill in all required fields."

        # Style Checkboxes
        self.late_rides_cb = PaintedCheckBox("Late rides")
        self.late_rides_cb.setChecked(account.late_rides)

        self.long_rides_cb = PaintedCheckBox("Long rides")
        self.batteries_cb = PaintedCheckBox("Batteries")
        self.long_rides_cb.setChecked(account.long_rides)
        self.batteries_cb.setChecked(account.batteries)

        self.pointer_cb = PaintedCheckBox("Pointer")
        self.pointer_cb.setChecked(account.pointer)
        self.pointer_cb.setToolTip("Enable Pointer integration for ride management.")
        self.pointer_cb.setDisabled(self.long_rides_cb.isChecked() or self.batteries_cb.isChecked())

        self.pointer_user_input = QLineEdit()
        self.pointer_user_input.setPlaceholderText("Enter Pointer username")
        self.pointer_user_input.setText(account.pointer_user)
        self.pointer_user_input.setVisible(account.pointer)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Enter phone number")
        self.phone_input.setText(account.phone)
        self.phone_input.setVisible(account.pointer)
        self.setObjectName("settingsPanel")
        self.setAutoFillBackground(True)

        self.setStyleSheet("""
            QWidget#settingsPanel {background-color: #fefcfd;}
            QWidget {
                font-family: "Segoe UI", "Tahoma", "Arial";
                font-size: 16px;
            }
            QLabel {
                font-weight: 500;
                color: #1f1f1f;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                margin-top: 24px;
                margin-left: 20px;
                font-size: 18px;
                font-weight: semibold;
                }

            QGroupBox {
                border: none;
                background-color: #fefcfd;
                border-radius: 6px;
                padding: 12px 14px;
                padding-top: 24px;
                margin-top: 16px;
            }
            QLineEdit {
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: #fafafa;
                font-size: 15px;
            }
            QLineEdit:focus {
                border: 1px solid #4a90e2;
                background-color: #fefcfd;
            }
            QCheckBox {
                margin-top: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                image: url(:/qt-project.org/styles/commonstyle/images/checkbox_checked.png);
                border: 1px solid #4a90e2;
            }
            QCheckBox::indicator:hover {
                border: 1px solid #4a90e2;
            }
        """)

        # Signals
        self.pointer_cb.stateChanged.connect(self.toggle_phone_input)
        self.long_rides_cb.stateChanged.connect(self.toggle_pointer)
        self.batteries_cb.stateChanged.connect(self.toggle_pointer)

        # Group: Goto
        goto_group = QGroupBox("Goto")
        goto_layout = QVBoxLayout()
        goto_layout.addWidget(self.late_rides_cb)
        goto_group.setLayout(goto_layout)
        self.add_shadow(goto_group)

        # Group: AutoTel
        autot_group = QGroupBox("AutoTel")
        autot_layout = QVBoxLayout()
        autot_layout.addWidget(self.long_rides_cb)
        autot_layout.addWidget(self.batteries_cb)
        autot_group.setLayout(autot_layout)
        self.add_shadow(autot_group)

        # Group: Others
        others_group = QGroupBox("Others")
        others_layout = QVBoxLayout()
        pointer_layout = QHBoxLayout()
        self.pointer_cb.setStyleSheet("margin: 0;")
        pointer_layout.addWidget(self.pointer_cb)
        pointer_layout.addWidget(self.pointer_user_input)
        pointer_layout.addWidget(self.phone_input)
        others_layout.addLayout(pointer_layout)
        others_group.setLayout(others_layout)
        self.add_shadow(others_group)

        # Main layout
        layout = QVBoxLayout()
        header_label = QLabel("Settings")
        header_label.setStyleSheet("font-size: 20px; font-weight: 600;")
        layout.addWidget(header_label)
        layout.addWidget(goto_group)
        layout.addWidget(autot_group)
        layout.addWidget(others_group)
        layout.addStretch()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        self.setLayout(layout)

    def add_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)         # Soft blur
        shadow.setOffset(0, 3)           # Slight downward offset
        shadow.setColor(QColor(0, 0, 0, 20))  # Soft black shadow with transparency
        widget.setGraphicsEffect(shadow)


    def toggle_phone_input(self, state):
        data_visible = state == Qt.CheckState.Checked.value
        self.pointer_user_input.setVisible(data_visible)
        self.phone_input.setVisible(data_visible)
        
    def toggle_pointer(self, state):
        self.pointer_cb.setChecked(self.long_rides_cb.isChecked() or self.batteries_cb.isChecked() or self.pointer_cb.isChecked())
        self.pointer_cb.setDisabled(self.long_rides_cb.isChecked() or self.batteries_cb.isChecked())

    def is_valid(self):
        import re
        return (
            not self.pointer_cb.isChecked()
            or bool(re.fullmatch(r"^\d{10}$", self.phone_input.text().strip()))
        )


    def get_data(self):
        return {
            "late_rides": self.late_rides_cb.isChecked(),
            "long_rides": self.long_rides_cb.isChecked(),
            "batteries": self.batteries_cb.isChecked(),
            "pointer": self.pointer_cb.isChecked(),
            "pointer_user": self.pointer_user_input.text() if self.pointer_cb.isChecked() else None,
            "phone": self.phone_input.text() if self.pointer_cb.isChecked() else None,
        }
