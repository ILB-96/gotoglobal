
import asyncio
from PyQt6.QtCore import pyqtSignal, pyqtSlot, QThread


class BaseWorker(QThread):
    def __init__(self, parent=None):
        super(BaseWorker, self).__init__(parent)
        self.stop_event = asyncio.Event()
        self.running = True
        
    @pyqtSlot()
    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._async_main())
        self.loop.close()
    
    async def _async_main(self):
        raise NotImplementedError("Subclasses should implement this method")
            
    def trigger_stop_event(self):
        if self.loop:
            self.loop.call_soon_threadsafe(self.stop_event.set)
            
    async def wait_by(self, timeout=None):
        """
        Waits for the stop_event to be set, or until timeout (in seconds).
        The timeout parameter is in seconds.
        """
        try:
            await asyncio.wait_for(self.stop_event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            pass
        self.stop_event.clear()

    async def event_wait(self):
        """Waits indefinitely until the stop_event is set."""
        await self.stop_event.wait()
        self.stop_event.clear()
        
    def stop(self):
        self.running = False
        self.stop_event.set()