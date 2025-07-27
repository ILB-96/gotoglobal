from queue import Queue
import re
import threading
from typing import Dict, List, Literal
import uuid

import httpx
import settings
from src.shared import utils
from src.workers.base_worker import BaseWorker
from PyQt6.QtCore import pyqtSignal, pyqtSlot
import traceback
from datetime import datetime as dt, timedelta

class WebNotificationWorker(BaseWorker):
    """Worker for handling web notifications."""
    toast_signal = pyqtSignal(str, str, str)
    request_cookies = pyqtSignal(str)
    def __init__(self, parent=None):
        super(WebNotificationWorker, self).__init__(parent)
        self.queue = Queue()
        
        
        self._cookies_condition = threading.Condition()
        self._goto_cookies = None
        self._autotel_cookies = None
    
    async def _async_main(self):
        await self.event_wait()
        while self.running:
            while not self.queue.empty():
                
                mode, data = self.queue.get_nowait()
                if mode == 'goto':
                    await self.handle_goto_notification(data)
                elif mode == 'autotel':
                    await self.handle_autotel_notification(data)
                else:
                    print(f"Unknown mode: {mode}")
            print("Waiting for new notifications...")
            await self.event_wait()

    async def handle_goto_notification(self, data: Dict):
        """Handle Goto notifications."""
        # Process Goto notifications
        notified_on = data.get('modifiedon@OData.Community.Display.V1.FormattedValue')
        
        if self.is_notification_expired(notified_on):
            return
        cookies = self.request_cookies_sync('goto')
        notification_id = data.get('body', 'id=1').split('id=')[-1].strip(')')
        msg = await self.fetch_batch_data('goto', cookies, notification_id)
        title = data.get('title', 'No Title')
        created_on = data.get('createdon', 'Unknown Date')
        
        license_plate_match = re.search(r'\b\d{3}-\d{2}-\d{3}\b', msg or "")
        license_plate = license_plate_match.group() if license_plate_match else None

        print("First License Plate:", license_plate)
        print('msg: ', msg, 'title:', title, 'license_plate:', license_plate, 'created_on:', created_on)

        self.toast_signal.emit(
            title,
            f"{created_on}\nLicense Plate: {license_plate or 'N/A'}",
            utils.resource_path(settings.app_icon)
        )

    def is_notification_expired(self, notified_on):
        return not notified_on or dt.strptime(notified_on, '%d/%m/%Y %H:%M') < dt.now() - timedelta(minutes=2)

    async def handle_autotel_notification(self, data: Dict):
        """Handle Autotel notifications."""
        # Process Autotel notifications
        notified_on = data.get('modifiedon@OData.Community.Display.V1.FormattedValue')
        is_battery_notification = 'סוללה' in data.get('title', '')
        if self.is_notification_expired(notified_on) or is_battery_notification:
            return
        cookies = self.request_cookies_sync('autotel')
        notification_id = data.get('body', 'id=1').split('id=')[-1].strip(')')
        msg = await self.fetch_batch_data('autotel', cookies, notification_id)
        
        title = data.get('title', 'No Title')
        created_on = data.get('createdon@OData.Community.Display.V1.FormattedValue', 'Unknown Date')
        
        license_plate_match = re.search(r'\b\d{3}-\d{2}-\d{3}\b', msg or "")
        license_plate = license_plate_match.group() if license_plate_match else None

        print("First License Plate:", license_plate)
        print('msg: ', msg, 'title:', title, 'license_plate:', license_plate, 'created_on:', created_on)

        self.toast_signal.emit(
            title,
            f"{notified_on}\nLicense Plate: {license_plate or 'N/A'}",
            utils.resource_path(settings.autotel_icon)
        )

    def enqueue_notification(self, mode: str, data: List):
        """Handle notifications based on the mode (goto or autotel)."""
        """Enqueue a notification for processing."""
        print(f"Enqueuing notification for mode: {mode})")
        self.queue.put((mode, data))
        self.trigger_stop_event()
        
    def request_cookies_sync(self, mode: Literal['goto', 'autotel']) -> object:
        """Emit signal and wait for location data."""
        if mode == 'goto':
            self._goto_cookies = None
        elif mode == 'autotel':
            self._autotel_x_token = None
        with self._cookies_condition:
            self.request_cookies.emit(mode)
            if not self._cookies_condition.wait(timeout=70):
                return
        return self._goto_cookies if mode == 'goto' else self._autotel_cookies

            
    def set_cookies_data(self, mode, data):
        """Receives location data from WebDataWorker."""
        with self._cookies_condition:
            if mode == 'goto':
                self._goto_cookies = data
            elif mode == 'autotel':
                self._autotel_cookies = data
            self._cookies_condition.notify()
    
    async def fetch_batch_data(self, mode, cookie, notification_id='27b54f82-ee5d-f011-bec2-7c1e5283c999'):
        BATCH_ID = f"batch_{uuid.uuid4().hex}"

        BATCH_BODY = (
            f"--{BATCH_ID}\r\n"
            "Content-Type: application/http\r\n"
            "Content-Transfer-Encoding: binary\r\n"
            "\r\n"
            f"GET /api/data/v9.0/emails({notification_id})?$select=safedescription HTTP/1.1\r\n"
            "Accept: application/json\r\n"
            "\r\n"
            f"--{BATCH_ID}--\r\n"
        )

        url = f"https://{mode}.crm4.dynamics.com/api/data/v9.0/$batch"
        headers = {
            "Content-Type": f"multipart/mixed;boundary={BATCH_ID}",
            "Accept": "application/json",
            "Cookie": cookie
        }
        print(f"url: {url}, headers: {headers}, body: {BATCH_BODY}")


        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, content=BATCH_BODY.encode())
                response.raise_for_status()
                return response.text
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e.response.status_code} - {e.response}")
        except Exception as e:
            print(f"Other error: {e}")
            traceback.print_exc()