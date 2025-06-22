from pathlib import Path
from services.fluent.qfluentwidgets.components.settings.setting_card import SettingCard
from src.frontend import Input, SettingsPanel
from services import PopupWindow
from src.shared import utils, User
import settings
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QSizePolicy, QFrame
from services.fluent.qfluentwidgets import (ScrollArea, LineEditSettingCard,
    SettingCardGroup, SwitchSettingCard, FluentWindow, PrimaryPushSettingCard, ExpandLayout, FluentIcon as FIF, NavigationItemPosition
    
)
from PyQt6.QtCore import Qt, pyqtSignal, QEventLoop
from src.app.common.style_sheet import StyleSheet
class TwoColumnSettingCard(QFrame):
    def __init__(self, card1: QWidget, card2: QWidget, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        card1.setFixedWidth(263)
        card2.setFixedWidth(217)
        layout.addWidget(card1)
        layout.addWidget(card2)

        # Style similar to other cards
        self.setFixedHeight(50)
        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
            }
        """)
class SettingsInterface(ScrollArea):
    confirmed = pyqtSignal()  # Signal to notify when user confirms 

    def __init__(self, user: User, parent=None):
        super().__init__(parent)

        self.user = user

        # Central widget and layout
        self.scrollWidget = QWidget(self)
        self.layout = ExpandLayout(self.scrollWidget)
        self.settingLabel = QLabel(self.tr("Settings"), self)

        # Group 1: Ride settings
        self.gotoGroup = SettingCardGroup("Goto", self.scrollWidget)
        self.lateRidesCard = SwitchSettingCard(
            FIF.CAR, "Late Rides", "Enable alerts for late rides", user.late_rides, self.gotoGroup
        )

        self.autotelGroup = SettingCardGroup("AutoTel", self.scrollWidget)
        self.longRidesCard = SwitchSettingCard(
            FIF.DATE_TIME, "Long Rides", "Enable alerts for long rides", user.long_rides, self.autotelGroup
        )
        self.batteriesCard = SwitchSettingCard(
            FIF.SPEED_OFF, "Battery Alerts", "Enable alerts for low battery", user.batteries, self.autotelGroup
        )

        self.othersGroup = SettingCardGroup("Others", self.scrollWidget)
        self.pointerCard = SwitchSettingCard(
            FIF.GLOBE, "Pointer (Required for Autotel)", "Enable Pointer location integration", 
            user.pointer, self.othersGroup
        )
        self.pointerUserCard = LineEditSettingCard(
            '', "Username", '', user.pointer_user, self.othersGroup
        )
        self.pointerPhoneCard = LineEditSettingCard(
            '', "Phone", '', user.phone, self.othersGroup
        )

        self.pointerRowCard = TwoColumnSettingCard(self.pointerUserCard, self.pointerPhoneCard, self.othersGroup)

        self.saveBtn = PrimaryPushSettingCard(
            text="Let's Go!",
            title="Apply Settings",
            icon=FIF.SAVE,
            content="Click to apply and close the window",
            parent=self.scrollWidget
        )
        self.saveBtn.clicked.connect(self._on_save_clicked)
        self.__initWidget()
        self.__initLayout()

        # # Use layout in this widget
        # wrapper = QVBoxLayout(self)
        # wrapper.addWidget(self.scrollWidget)
        
    def __initWidget(self):
            self.resize(1000, 800)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.setViewportMargins(0, 80, 0, 20)
            self.setWidget(self.scrollWidget)
            self.setWidgetResizable(True)
            self.setObjectName('settingInterface')

            # initialize style sheet
            self.scrollWidget.setObjectName('scrollWidget')
            self.settingLabel.setObjectName('settingLabel')
            StyleSheet.SETTING_INTERFACE.apply(self)
    
    def __initLayout(self):
        self.settingLabel.move(36, 30)

        # Add cards to groups
        self.gotoGroup.addSettingCard(self.lateRidesCard)
        self.autotelGroup.addSettingCard(self.longRidesCard)
        self.autotelGroup.addSettingCard(self.batteriesCard)
        self.othersGroup.addSettingCard(self.pointerCard)
        if self.user.pointer.value:
            self.othersGroup.addSettingCard(self.pointerRowCard)

        self.pointerCard.checkedChanged.connect(self.toggle_pointer_row)
        self.longRidesCard.checkedChanged.connect(self.enforce_pointer_required)
        self.batteriesCard.checkedChanged.connect(self.enforce_pointer_required)
        self.enforce_pointer_required()
        
        self.layout.setSpacing(28)
        self.layout.setContentsMargins(36, 10, 36, 0)
        self.layout.addWidget(self.gotoGroup)
        self.layout.addWidget(self.autotelGroup)
        self.layout.addWidget(self.othersGroup)
        self.layout.addWidget(self.saveBtn)

    def toggle_pointer_row(self, is_enabled: bool):
        print("Pointer enabled, adding row card")
        self.pointerPhoneCard.setDisabled(not is_enabled)
        self.pointerUserCard.setDisabled(not is_enabled)
    
    def toggle_pointer_row(self, is_enabled: bool):
        long_on = self.longRidesCard.isChecked()
        batt_on = self.batteriesCard.isChecked()

        if not is_enabled and (long_on or batt_on):
            # Not allowed to disable pointerCard while dependencies are active
            self.pointerCard.setChecked(True)
            return

        # Toggle input fields for pointer details
        self.pointerUserCard.setDisabled(not is_enabled)
        self.pointerPhoneCard.setDisabled(not is_enabled)


    def enforce_pointer_required(self):
        long_on = self.longRidesCard.isChecked()
        batt_on = self.batteriesCard.isChecked()

        if long_on or batt_on:
            # Force-enable pointerCard if required
            self.pointerCard.setChecked(True)
            self.pointerCard.setDisabled(True)
        else:
            self.pointerCard.setDisabled(False)
    def _on_save_clicked(self):
        # Emit confirmed signal and close window
        self.confirmed.emit()
        self.window().close()


class SettingsPopup(FluentWindow):
    def __init__(self, user: User, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Settings")
        self.setFixedSize(560, 600)
        self.settingsPage = SettingsInterface(user, self)
        self.hBoxLayout.removeWidget(self.navigationInterface)
        self.navigationInterface.hide()
        self.addSubInterface(self.settingsPage, FIF.SETTING, "Settings", position=NavigationItemPosition.TOP)
        self.loop = QEventLoop()
        # Connect confirmed signal to handler
        self.settingsPage.confirmed.connect(self.on_settings_confirmed)
        
    def exec(self):
        """ Mimic modal behavior like QDialog.exec() """
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.show()
        self.loop.exec()  # blocks here

    def on_settings_confirmed(self):
        updated_user = self.get_updated_user()
        updated_user.to_json(settings.user_json_path)
        self.loop.quit()
        self.close()
        
    def get_updated_user(self) -> User:
        sp = self.settingsPage
        self.user.late_rides = sp.lateRidesCard.isChecked()
        self.user.long_rides = sp.longRidesCard.isChecked()
        self.user.batteries = sp.batteriesCard.isChecked()
        self.user.pointer = sp.pointerCard.isChecked()
        self.user.pointer_user = sp.pointerUserCard.geValue()
        self.user.phone = sp.pointerPhoneCard.geValue()
        return self.user


def handle_settings_input(account: User):
    dialog = SettingsPopup(account)
    dialog.exec()  # This blocks until the dialog is closed

def handle_code_input(worker):
    cta = """
    <h2>We need to connect you to Pointer for location data</h2>
    <p>
    Please enter the code sent to your phone number.
    </p>
    """
    line_edit = Input(
        title="code",
        placeholder="Enter 6-digit code",
        validator=r"^\d{6}$",
        error_message="Code must be 6 digits"
    )
    popup = PopupWindow(
        cta,
        icon=utils.resource_path(settings.app_icon),
        widgets=[line_edit],
    )
    data = popup.get_input()
    worker.input_received.emit({ **data })

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