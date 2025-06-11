import os
from pathlib import Path
import sys
from PyQt6.QtWidgets import QApplication
from services import TinyDatabase
from services import window, popup_window
import settings
from src.frontend import setup_tabs_and_tables, Input, SettingsPanel, PlaywrightWorker
import traceback
from PyQt6.QtWidgets import QMessageBox

from src.shared import utils

def setup_shared_resources():
    return TinyDatabase({
        "autotel": ["autotelDB.json", "ride_id"],
        "goto": ["gotoDB.json", "ride_id"],
        "user": ["userDB.json", "username"],
    })

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
    popup = popup_window.PopupWindow(
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
    popup = popup_window.PopupWindow(
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

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        main_win = window.MainWindow(title="GotoGlobal", app_icon=utils.resource_path(settings.app_icon))
        
        db = setup_shared_resources()
    
        tables = setup_tabs_and_tables(main_win)

        worker = PlaywrightWorker(db)
        worker.signals.toast_signal.connect(main_win.show_toast)
        worker.signals.late_table_row.connect(tables['late_rides'].add_rows)
        worker.signals.batteries_table_row.connect(tables['batteries'].add_rows)
        worker.signals.long_rides_table_row.connect(tables['long_rides'].add_rows)
        worker.signals.request_settings_input.connect(lambda: handle_settings_input(worker))
        worker.signals.request_otp_input.connect(lambda: handle_code_input(worker))
        worker.signals.input_received.connect(worker.set_account_data)
        worker.signals.start_loading.connect(lambda: handle_start_loading(tables))
        worker.signals.stop_loading.connect(lambda: handle_stop_loading(tables))

        main_win.threadpool.start(worker)
        app.aboutToQuit.connect(worker.stop)
        # handle_settings_input(worker)
        # rows = [["12313", "12/12/2023 12:00", ("Future Ride", lambda: print("Open Future Ride")), "12/12/2023 13:00"],
        #         ["12314", "12/12/2023 12:30", ("Future Ride", lambda: print("Open Future Ride")), "12/12/2023 13:30"]]
        
        # tables['late_rides'].add_rows(rows, btn_colors=("#1d5cd0", "#392890", "#1f1f68"))


        main_win.show()
        sys.exit(app.exec())
    except Exception as e:

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Startup Error")
        msg.setText("An error occurred:")
        msg.setDetailedText(traceback.format_exc())
        msg.exec()
