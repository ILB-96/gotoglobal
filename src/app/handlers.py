from src.frontend import Input
from services import PopupWindow
from src.shared import utils
import settings
from .view.settings_interface import SettingsPopup
def handle_settings_input():
    dialog = SettingsPopup()
    dialog.exec()

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