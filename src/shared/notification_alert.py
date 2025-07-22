
from src.shared import utils
from . import BaseAlert


class NotificationAlert(BaseAlert):
    """
    Class for handling notifications.
    """
    def __init__(self, show_toast, gui_table_row, open_ride, x_token_request):
        super().__init__(show_toast, gui_table_row, open_ride, x_token_request)

    async def add_notification(self, x_token: str, data: dict):
        """
        Starts the requests to fetch notifications.
        """
        self.x_token = x_token

        car_info = await self.fetch_car_info(data.get('license_plate', ''))

        if not car_info:
            self.show_toast("No car information found for the license plate.")
            return
    
    async def fetch_car_info(self, license_plate: str):
        """
        Fetches car information based on the license plate.
        """
        if not license_plate:
            return None
        
        url = 'https://car2gopublicapi.gototech.co/API/SEND'
        payload = {
            "Username": "x",
            "Password": "x",
            "Opcode": "GetCarInfo",
            "Data": license_plate
        }
        
        try:
            data = await utils.fetch_data(url, self.x_token, payload)
            return data.get('Data', {})
        except Exception as e:
            print(f"Error fetching car info: {e}")
            return None