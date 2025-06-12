from services import MainWindow
from src.frontend import setup_tabs_and_tables, PlaywrightWorker
import settings
from src.shared import utils

from handlers import (
    handle_settings_input,
    handle_code_input,
    handle_start_loading,
    handle_stop_loading,
)
from services import TinyDatabase

def setup_shared_resources():
    return TinyDatabase({
        "autotel": ["autotelDB.json", "ride_id"],
        "goto": ["gotoDB.json", "ride_id"],
        "user": ["userDB.json", "username"],
    })

def start_app(app):
    main_win = MainWindow(title="GotoGlobal", app_icon=utils.resource_path(settings.app_icon))
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
    main_win.show()
    app.exec()