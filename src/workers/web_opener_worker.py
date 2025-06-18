from pathlib import Path
from queue import Queue
import threading
from PyQt6.QtCore import pyqtSignal, pyqtSlot, QThread

from playwright.sync_api import sync_playwright
from services import WebAccess
import settings
from src.autotel import BatteriesAlert, LongRides
from src.goto import LateAlert
from src.shared import PointerLocation, User
import time

class WebAutomationWorker(QThread):
    page_loaded = pyqtSignal()

    open_url_requested = pyqtSignal(str)
    request_settings_input = pyqtSignal()
    request_otp_input = pyqtSignal()
    input_received = pyqtSignal(object)

    start_loading = pyqtSignal()
    stop_loading = pyqtSignal()
    def __init__(self, account: User, parent=None):
        super(WebAutomationWorker, self).__init__(parent)
        self.stop_event = threading.Event()
        self.running = True
        self.url_queue = Queue()
        self.open_url_requested.connect(self.enqueue_url)
        self.account = account

    @pyqtSlot()
    def run(self):