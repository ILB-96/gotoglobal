from src.workers import WebDataWorker, WebAutomationWorker
import settings
from src.shared import utils
from src.workers.web_notification_worker import WebNotificationWorker

from .handlers import (
    handle_settings_input,
    handle_code_input,
)
from .view.main_window import MainWindow


def start_app(app):

    # create main window
    main_win = MainWindow(title="GotoGlobal", app_icon=utils.resource_path(settings.app_icon))
    

    handle_settings_input()

    web_data_worker = WebDataWorker()
    web_automation_worker = WebAutomationWorker()
    web_notification_worker = WebNotificationWorker()
    
    create_web_notification_worker(web_notification_worker, web_data_worker)
    create_web_automation_worker(main_win, web_automation_worker, web_data_worker)
    create_web_data_worker(web_data_worker, web_automation_worker, web_notification_worker)

    
    
    app.aboutToQuit.connect(web_automation_worker.stop)
    app.aboutToQuit.connect(web_data_worker.stop)

    main_win.show()
    app.exec()
    
def create_web_notification_worker(worker: WebNotificationWorker, web_data_worker: WebDataWorker):
    worker.start()
    web_data_worker.notification_send.connect(worker.enqueue_notification)
    worker.request_cookies.connect(web_data_worker.enqueue_cookies)
    
def create_web_data_worker(worker: WebDataWorker, web_automation_worker: WebAutomationWorker, 
                           web_notification_worker: WebNotificationWorker):
    worker.start()
    worker.request_otp_input.connect(lambda: handle_code_input(worker))
    worker.x_token_send.connect(web_automation_worker.set_x_token_data)
    worker.pointer_location_send.connect(web_automation_worker.set_location_data)
    worker.input_received.connect(worker.trigger_stop_event)
    worker.page_loaded.connect(web_automation_worker.trigger_stop_event)
    worker.cookies_send.connect(web_notification_worker.set_cookies_data)



def create_web_automation_worker(main_win, worker: WebAutomationWorker, web_data_worker: WebDataWorker):
    worker.start()
    worker.toast_signal.connect(main_win.show_toast)
    worker.late_table_row.connect(main_win.gotoInterface.late_rides_table.setRows)
    worker.batteries_table_row.connect(main_win.autotelInterface.batteries_table.setRows)
    worker.long_rides_table_row.connect(main_win.autotelInterface.long_rides_table.setRows)
    worker.request_delete_table.connect(main_win.removeWidgets)
    # worker.request_delete_tab.connect(lambda tab: main_win.delete_tab(tab))
    worker.request_x_token.connect(web_data_worker.enqueue_x_token)
    worker.request_pointer_location.connect(web_data_worker.enqueue_pointer_location)
    worker.open_url_requested.connect(web_data_worker.enqueue_url)
