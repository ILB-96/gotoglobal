from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel, QLineEdit, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt


class SettingsPanel(QWidget):
    def __init__(self, parent=None, account=None):
        super().__init__(parent)

        if account is None:
            account = {}
        
        self.error_message = "Please fill in all required fields."

        self.late_rides_cb = QCheckBox("Late rides")
        self.late_rides_cb.setChecked(account.get("late_rides", True))

        self.long_rides_cb = QCheckBox("Long rides")
        self.batteries_cb = QCheckBox("Batteries")
        self.long_rides_cb.setChecked(account.get("long_rides", True))
        self.batteries_cb.setChecked(account.get("batteries", True))

        self.pointer_cb = QCheckBox("Pointer")
        self.pointer_cb.setChecked(account.get("pointer", True))
        self.pointer_cb.setToolTip("Enable Pointer integration for ride management.")
        self.pointer_cb.setDisabled(self.long_rides_cb.isChecked() or self.batteries_cb.isChecked())

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Enter phone number")
        self.phone_input.setText(account.get("phone", ""))
        self.phone_input.setVisible(account.get("pointer", True))

        self.setStyleSheet("""
            QWidget {
                font-family: 'Tahoma', "Arial";
                font-size: 16px;
            }
            QGroupBox {
                border: 1px solid #dcdcdc;
                border-radius: 4px;
                margin-top: 16px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 0 5px;
                font-weight: bold;
                color: #333;
                margin-top: 5px;
            }
            QLabel {
                font-weight: 600;
                margin-bottom: 2px;
            }
            QLineEdit {
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 16px;
            }
            QLineEdit:focus {
                border: 1px solid #4caf50;
                background-color: #f9fff9;
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

        # Group: AutoTel
        autot_group = QGroupBox("AutoTel")
        autot_layout = QVBoxLayout()
        autot_layout.addWidget(self.long_rides_cb)
        autot_layout.addWidget(self.batteries_cb)
        autot_group.setLayout(autot_layout)

        # Group: Others
        others_group = QGroupBox("Others")
        others_layout = QVBoxLayout()
        pointer_layout = QHBoxLayout()
        pointer_layout.addWidget(self.pointer_cb)
        pointer_layout.addWidget(self.phone_input)
        others_layout.addLayout(pointer_layout)
        others_group.setLayout(others_layout)

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel("<h3>Settings:</h3>"))
        layout.addWidget(goto_group)
        layout.addWidget(autot_group)
        layout.addWidget(others_group)
        layout.addStretch()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        self.setLayout(layout)



    def toggle_phone_input(self, state):
        self.phone_input.setVisible(state == Qt.CheckState.Checked.value)
        
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
            "phone": self.phone_input.text() if self.pointer_cb.isChecked() else None,
        }
