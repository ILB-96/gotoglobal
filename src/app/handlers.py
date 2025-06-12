from pathlib import Path
from src.frontend import Input, SettingsPanel
from services import PopupWindow
from src.shared import utils
import settings

def handle_settings_input(worker):
    username = Path.home().name
    cta = f"""
    <h2>Hey {username.replace('.', ' ').title()},</h2>
    <p>
    Welcome to your GOTO service companion!
    <br>
    </p>
    """
    settings_panel = SettingsPanel(account=worker.account)
    popup = PopupWindow(
        cta,
        icon=utils.resource_path(settings.app_icon),
        widgets=[settings_panel]
    )
    data = popup.get_input()
    worker.signals.input_received.emit({ "username": username, **data})

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
    worker.signals.input_received.emit({ **data })

def handle_start_loading(tables):
    for table in tables.values():
        table.start_loading()

def handle_stop_loading(tables):
    for table in tables.values():
        table.stop_loading()