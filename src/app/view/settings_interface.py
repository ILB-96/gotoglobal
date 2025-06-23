from services.fluent.qfluentwidgets import (ScrollArea, LineEditSettingCard,
    SettingCardGroup, SwitchSettingCard, FluentWindow, PrimaryPushSettingCard, ExpandLayout, FluentIcon as FIF
    
)
from PyQt6.QtGui import QKeySequence, QShortcut

from PyQt6.QtCore import Qt, pyqtSignal, QEventLoop
from src.app.common.style_sheet import StyleSheet
from ..common.config import cfg
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget
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

    def __init__(self, parent=None):
        super().__init__(parent)

        # Central widget and layout
        self.scrollWidget = QWidget(self)
        self.layout = ExpandLayout(self.scrollWidget)
        self.settingLabel = QLabel(self.tr("Settings"), self)

        # Group 1: Ride settings
        self.gotoGroup = SettingCardGroup("Goto", self.scrollWidget)
        self.lateRidesCard = SwitchSettingCard(
            FIF.CAR, "Late Rides", "Enable alerts for late rides", cfg.late_rides, self.gotoGroup
        )
        self.createGotoTabsCard = SwitchSettingCard(
            FIF.QUICK_NOTE, "Create Goto pages", "Create Goto BO & CRM (if don't already exists)", cfg.create_goto_tabs, self.gotoGroup
        )

        self.autotelGroup = SettingCardGroup("AutoTel", self.scrollWidget)
        self.longRidesCard = SwitchSettingCard(
            FIF.DATE_TIME, "Long Rides", "Enable alerts for long rides", cfg.long_rides, self.autotelGroup
        )
        self.batteriesCard = SwitchSettingCard(
            FIF.SPEED_OFF, "Battery Alerts", "Enable alerts for low battery", cfg.batteries, self.autotelGroup
        )
        self.createAutotelTabsCard = SwitchSettingCard(
            FIF.QUICK_NOTE, "Create Autotel pages", "Create Autotel BO & CRM tabs (if don't already exists)", cfg.create_autotel_tabs, self.autotelGroup
        )

        self.othersGroup = SettingCardGroup("Others", self.scrollWidget)
        self.pointerCard = SwitchSettingCard(
            FIF.GLOBE, "Pointer (Required for Autotel)", "Enable Pointer location integration", 
            cfg.pointer, self.othersGroup
        )
        self.pointerUserCard = LineEditSettingCard(
            '', "Username", '', cfg.pointer_user, self.othersGroup
        )
        self.pointerPhoneCard = LineEditSettingCard(
            '', "Phone", '', cfg.phone, self.othersGroup
        )

        self.pointerRowCard = TwoColumnSettingCard(self.pointerUserCard, self.pointerPhoneCard, self.othersGroup)

        self.saveBtn = PrimaryPushSettingCard(
            text="Let's Go!",
            title="Apply Settings",
            icon=FIF.SAVE,
            content="Click to apply and close the window",
            parent=self.scrollWidget
        )
        return_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        enter_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Enter), self)
        return_shortcut.activated.connect(self.saveBtn.clicked)
        enter_shortcut.activated.connect(self.saveBtn.clicked)
        self.saveBtn.clicked.connect(self._on_save_clicked)
        self.__initWidget()
        self.__initLayout()

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
        self.gotoGroup.addSettingCard(self.createGotoTabsCard)
        self.autotelGroup.addSettingCard(self.longRidesCard)
        self.autotelGroup.addSettingCard(self.batteriesCard)
        self.autotelGroup.addSettingCard(self.createAutotelTabsCard)
        self.othersGroup.addSettingCard(self.pointerCard)
        self.othersGroup.addSettingCard(self.pointerRowCard)

        self.pointerCard.checkedChanged.connect(self.toggle_pointer_row)
        self.longRidesCard.checkedChanged.connect(self.enforce_pointer_required)
        self.batteriesCard.checkedChanged.connect(self.enforce_pointer_required)
        self.enforce_pointer_required()
        self.toggle_pointer_row(self.pointerCard.isChecked())
        
        self.layout.setSpacing(28)
        self.layout.setContentsMargins(36, 10, 36, 0)
        self.layout.addWidget(self.gotoGroup)
        self.layout.addWidget(self.autotelGroup)
        self.layout.addWidget(self.othersGroup)
        self.layout.addWidget(self.saveBtn)

    def toggle_pointer_row(self, is_enabled: bool):
        long_on = self.longRidesCard.isChecked()
        batt_on = self.batteriesCard.isChecked()

        if not is_enabled and (long_on or batt_on):
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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(560, 600)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.titleBar.maxBtn.setParent(None)
        self.titleBar.maxBtn.deleteLater()
        self.titleBar.closeBtn.setParent(None)
        self.titleBar.closeBtn.deleteLater()

        self.setWindowIcon(FIF.SETTING.icon())
        self.settingsPage = SettingsInterface(self)
        self.hBoxLayout.removeWidget(self.navigationInterface)
        self.navigationInterface.hide()
        self.addSubInterface(self.settingsPage, '', "")
        self.loop = QEventLoop()
        self.settingsPage.confirmed.connect(self.on_settings_confirmed)
        
    def exec(self):
        """ Mimic modal behavior like QDialog.exec() """
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.show()
        self.loop.exec()

    def on_settings_confirmed(self):
        self.loop.quit()
        self.close()