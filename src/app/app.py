from pathlib import Path
from src.frontend import setup_tabs_and_tables
from src.workers import WebDataWorker, WebAutomationWorker
import settings
from src.shared import utils
from src.shared.user import User

from .handlers import (
    handle_settings_input,
    handle_code_input,
)
from .common.config import cfg
import os
import sys
from PyQt6.QtCore import Qt, QTranslator
from PyQt6.QtGui import QFont
from services.fluent.qfluentwidgets import FluentTranslator

from .view.main_window import MainWindow

if cfg.get(cfg.dpiScale) != "Auto":
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))


def start_app(app):

    # create main window
    main_win = MainWindow(title="GotoGlobal", app_icon=utils.resource_path(settings.app_icon))
    
    # tables = setup_tabs_and_tables(main_win)

    
    if (path := Path(settings.user_json_path)).exists():
        account = User.from_json(path)
    else:
        account = User()
    handle_settings_input(account)
    # account.to_json(settings.user_json_path)
    web_data_worker = WebDataWorker(account=account)
    web_automation_worker = WebAutomationWorker(account=account)
    
    create_web_data_worker(web_data_worker, web_automation_worker)

    create_web_automation_worker(main_win, web_automation_worker, web_data_worker)
    
    app.aboutToQuit.connect(web_automation_worker.stop)
    app.aboutToQuit.connect(web_data_worker.stop)
    # main_win.show()
    main_win.show()
    app.exec()

def create_web_data_worker(worker, web_automation_worker):
    worker.start()
    worker.request_otp_input.connect(lambda: handle_code_input(worker))
    worker.input_send.connect(lambda data: web_automation_worker.set_location_data(data))
    worker.input_received.connect(worker.set_account_data)
    worker.page_loaded.connect(web_automation_worker.stop_event.set)



def create_web_automation_worker(main_win, worker, web_data_worker):
    worker.start()
    worker.toast_signal.connect(main_win.show_toast)
    worker.late_table_row.connect(main_win.viewInterface.late_rides_table.setRows)
    worker.batteries_table_row.connect(main_win.viewInterface.batteries_table.setRows)
    worker.long_rides_table_row.connect(main_win.viewInterface.long_rides_table.setRows)
    worker.request_delete_table.connect(main_win.viewInterface.removeWidgets)
    # worker.request_delete_tab.connect(lambda tab: main_win.delete_tab(tab))
    worker.request_pointer_location.connect(lambda query: web_data_worker.enqueue_pointer_location(query))
    worker.open_url_requested.connect(lambda url: web_data_worker.enqueue_url(url))