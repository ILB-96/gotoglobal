from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QCheckBox, QLabel, QLineEdit, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt


class SettingsPanel(QWidget):
    def __init__(self, parent=None, account=None):
        super().__init__(parent)
        if account is None:
            account = {}

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

        # Signals
        self.pointer_cb.stateChanged.connect(self.toggle_phone_input)
        self.long_rides_cb.stateChanged.connect(self.toggle_pointer)
        self.batteries_cb.stateChanged.connect(self.toggle_pointer)
        
        # Group: Goto
        goto_group = QGroupBox("Goto:")
        goto_layout = QVBoxLayout()
        goto_layout.addWidget(self.late_rides_cb)
        goto_group.setLayout(goto_layout)

        # Group: AutoTel
        autot_group = QGroupBox("AutoTel:")
        autot_layout = QVBoxLayout()
        autot_layout.addWidget(self.long_rides_cb)
        autot_layout.addWidget(self.batteries_cb)
        autot_group.setLayout(autot_layout)

        # Group: Others
        others_group = QGroupBox("Others:")
        others_layout = QVBoxLayout()
        others_layout.addWidget(self.pointer_cb)
        others_layout.addWidget(self.phone_input)
        others_group.setLayout(others_layout)

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Settings:"))
        layout.addWidget(goto_group)
        layout.addWidget(autot_group)
        layout.addWidget(others_group)
        layout.addStretch()
        self.setLayout(layout)

    def toggle_phone_input(self, state):
        self.phone_input.setVisible(state == Qt.CheckState.Checked.value)
        
    def toggle_pointer(self, state):
        self.pointer_cb.setChecked(self.long_rides_cb.isChecked() or self.batteries_cb.isChecked() or self.pointer_cb.isChecked())
        self.pointer_cb.setDisabled(self.long_rides_cb.isChecked() or self.batteries_cb.isChecked())


    def get_data(self):
        return {
            "late_rides": self.late_rides_cb.isChecked(),
            "long_rides": self.long_rides_cb.isChecked(),
            "batteries": self.batteries_cb.isChecked(),
            "pointer": self.pointer_cb.isChecked(),
            "phone": self.phone_input.text() if self.pointer_cb.isChecked() else None,
        }
