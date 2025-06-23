from pathlib import Path
from src.workers import WebDataWorker, WebAutomationWorker
import settings
from src.shared import utils

from .handlers import (
    handle_settings_input,
    handle_code_input,
)
from .common.config import cfg

from .view.main_window import MainWindow


def start_app(app):

    # create main window
    main_win = MainWindow(title="GotoGlobal", app_icon=utils.resource_path(settings.app_icon))
    

    handle_settings_input()

    web_data_worker = WebDataWorker()
    web_automation_worker = WebAutomationWorker()
    
    create_web_data_worker(web_data_worker, web_automation_worker)

    create_web_automation_worker(main_win, web_automation_worker, web_data_worker)
    
    app.aboutToQuit.connect(web_automation_worker.stop)
    app.aboutToQuit.connect(web_data_worker.stop)

    main_win.show()
    app.exec()

def create_web_data_worker(worker, web_automation_worker):
    worker.start()
    worker.request_otp_input.connect(lambda: handle_code_input(worker))
    worker.input_send.connect(lambda data: web_automation_worker.set_location_data(data))
    worker.input_received.connect(worker.set_pointer_code)
    worker.page_loaded.connect(web_automation_worker.stop_event.set)



def create_web_automation_worker(main_win, worker, web_data_worker):
    worker.start()
    worker.toast_signal.connect(main_win.show_toast)
    worker.late_table_row.connect(main_win.gotoInterface.late_rides_table.setRows)
    worker.batteries_table_row.connect(main_win.autotelInterface.batteries_table.setRows)
    worker.long_rides_table_row.connect(main_win.autotelInterface.long_rides_table.setRows)
    worker.request_delete_table.connect(main_win.removeWidgets)
    # worker.request_delete_tab.connect(lambda tab: main_win.delete_tab(tab))
    worker.request_pointer_location.connect(lambda query: web_data_worker.enqueue_pointer_location(query))
    worker.open_url_requested.connect(lambda url: web_data_worker.enqueue_url(url))