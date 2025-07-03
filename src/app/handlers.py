
from .view.settings_interface import SettingsPopup
from .view.pointer_input_interface import PointerInputInterface

def handle_settings_input():
    dialog = SettingsPopup()
    dialog.exec()

def handle_code_input(worker):
    dialog = PointerInputInterface()
    dialog.exec()

    worker.input_received.emit()