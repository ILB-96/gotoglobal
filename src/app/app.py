from pathlib import Path
from services import MainWindow
from src.frontend import setup_tabs_and_tables
from src.workers import WebDataWorker, WebAutomationWorker
import settings
from src.shared import utils
from src.shared.user import User

from .handlers import (
    handle_settings_input,
    handle_code_input,
    handle_start_loading,
    handle_stop_loading,
)


def start_app(app):
    main_win = MainWindow(title="GotoGlobal", app_icon=utils.resource_path(settings.app_icon))
    tables = setup_tabs_and_tables(main_win)
    
    if (path := Path(settings.user_json_path)).exists():
        account = User.from_json(path)
    else:
        account = User()
    handle_settings_input(account)
    account.to_json(settings.user_json_path)
    web_data_worker = WebDataWorker(account=account)
    web_automation_worker = WebAutomationWorker(account=account)
    
    create_web_data_worker(web_data_worker, web_automation_worker)

    create_web_automation_worker(main_win, tables, web_automation_worker)
    
    app.aboutToQuit.connect(web_automation_worker.stop)
    main_win.show()
    app.exec()

def create_web_data_worker(worker, web_automation_worker):
    worker.start()
    worker.request_otp_input.connect(lambda: handle_code_input(worker))
    worker.input_send.connect(lambda data: web_automation_worker.set_location_data(data))
    worker.input_received.connect(worker.set_account_data)
    worker.page_loaded.connect(web_automation_worker.stop_event.set)



def create_web_automation_worker(main_win, tables, worker, web_data_worker):
    worker.start()
    worker.toast_signal.connect(main_win.show_toast)
    worker.late_table_row.connect(tables['late_rides'].add_rows)
    worker.batteries_table_row.connect(tables['batteries'].add_rows)
    worker.long_rides_table_row.connect(tables['long_rides'].add_rows)
    worker.input_received.connect(worker.set_account_data)
    worker.request_delete_table.connect(lambda tab, table: main_win.delete_table_from_tab(tab, table))
    worker.request_delete_tab.connect(lambda tab: main_win.delete_tab(tab))
    worker.request_pointer_location.connect(lambda query: web_data_worker.enqueue_pointer_location(query))
    worker.open_url_requested.connect(lambda url: web_data_worker.enqueue_url(url))