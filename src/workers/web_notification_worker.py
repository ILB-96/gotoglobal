from queue import Queue
from typing import List
from src.workers.base_worker import BaseWorker

class WebNotificationWorker(BaseWorker):
    """Worker for handling web notifications."""

    def __init__(self, parent=None):
        super(WebNotificationWorker, self).__init__(parent)
        self.queue = Queue()
    
    async def _async_main(self):
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
        self.stop_event.set()  # Trigger the event to process the queue