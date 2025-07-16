from queue import Queue
import threading
from typing import List, Literal
import uuid

import httpx
from src.workers.base_worker import BaseWorker
from PyQt6.QtCore import pyqtSignal, pyqtSlot


class WebNotificationWorker(BaseWorker):
    """Worker for handling web notifications."""
    request_cookies = pyqtSignal(str)
    def __init__(self, parent=None):
        super(WebNotificationWorker, self).__init__(parent)
        self.queue = Queue()
        
        
        self._cookies_condition = threading.Condition()
        self._goto_cookies = None
        self._autotel_cookies = None
    
    async def _async_main(self):
        data = self.request_cookies_sync('goto')
        print(f"Requesting cookies for mode: {data}")
        req = await self.fetch_batch_data(data)
        while self.running:
            while not self.queue.empty():
                mode, data = self.queue.get_nowait()
                if mode == 'goto':
                    await self.handle_goto_notification(data)
                elif mode == 'autotel':
                    await self.handle_autotel_notification(data)
                else:
                    print(f"Unknown mode: {mode}")

            await self.event_wait()

    async def handle_goto_notification(self, data: List):
        """Handle Goto notifications."""
        # Process Goto notifications
        print(f"Handling Goto notification with data: {data}")
        
    async def handle_autotel_notification(self, data: List):
        """Handle Autotel notifications."""
        # Process Autotel notifications
        print(f"Handling Autotel notification with data: {data}")
        
    def enqueue_notification(self, mode: str, data: List):
        """Handle notifications based on the mode (goto or autotel)."""
        """Enqueue a notification for processing."""
        print(f"Enqueuing notification for mode: {mode})")
        self.queue.put((mode, data))
        self.stop_event.set()
        
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
    
    async def fetch_batch_data(self, cookie, notification_id='5d8310af-4762-f011-bec3-6045bd8a1ab6'):
        BATCH_ID = f"batch_{uuid.uuid4().hex}"

        BATCH_BODY = f"""--{BATCH_ID}
            Content-Type: application/http
            Content-Transfer-Encoding: binary

            GET /api/data/v9.0/emails({notification_id})?$select=safedescription HTTP/1.1
            Accept: application/json
            """
        url = "https://goto.crm4.dynamics.com/api/data/v9.0/$batch"
        headers = {
            "Content-Type": f"multipart/mixed;boundary={BATCH_ID}",
            "Accept": "application/json",
            "Cookie": cookie
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, content=BATCH_BODY.encode())
                response.raise_for_status()
                print("resp:", response.text)
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e.response.status_code} - {e.response}")
        except Exception as e:
            print(f"Other error: {e}")