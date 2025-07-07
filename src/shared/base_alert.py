from services import AsyncWebAccess
from src.shared import utils


class BaseAlert:
    """
    Base class for alerts.
    """
    def __init__(self, show_toast, gui_table_row, web_access: AsyncWebAccess, open_ride, x_token_request):
        self.show_toast = show_toast
        self.gui_table_row = gui_table_row
        self.web_access = web_access
        self.open_ride = open_ride
        self.x_token_request = x_token_request

    async def start_requests(self):
        """
        Starts the requests to fetch alerts.
        This method should be overridden in subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")
    
    @utils.async_retry()
    async def init_page(self, page_name, url, default_url, timeout=250):
        page = await self.web_access.create_new_page(page_name, url, 'reuse')
        if 'login' in page.url:
            await page.goto(default_url, wait_until="networkidle")
            if url != default_url:
                await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(timeout)
        return page
    
    def build_ride_url(self, ride, default_url):
        return f'{default_url}/index.html#/orders/{ride}/details'