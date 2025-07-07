from functools import partial
import settings
from services import AsyncWebAccess

from src.pages import CarsPage, RidePage

from src.shared import utils
from src.shared import BaseAlert

class BatteriesAlert(BaseAlert):
    def __init__(self, show_toast, gui_table_row, web_access: AsyncWebAccess, pointer, open_ride, x_token_request):
        super().__init__(
            show_toast=show_toast,
            gui_table_row=gui_table_row,
            open_ride=open_ride,
            x_token_request=x_token_request
        )
        self.pointer = pointer
        
    async def start_requests(self, x_token: str):
        self.x_token = x_token
        