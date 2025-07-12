import json
from services import AsyncWebAccess
from src.shared import utils


class BaseAlert:
    """
    Base class for alerts.
    """
    def __init__(self, show_toast, gui_table_row, open_ride, x_token_request):
        self.show_toast = show_toast
        self.gui_table_row = gui_table_row
        self.open_ride = open_ride
        self.x_token_request = x_token_request
        self.x_token = ""

    async def start_requests(self, x_token: str):
        """
        Starts the requests to fetch alerts.
        This method should be overridden in subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")
    
    def build_ride_url(self, ride, default_url):
        return f'{default_url}/index.html#/orders/{ride}/details'
    
    async def get_ride_comment(self, ride_id: str, service_name: str, url: str) -> str:
        """
        Fetches the ride comment from the Autotel API.
        
        Args:
            ride_id (str): The ID of the ride.
            x_token (str): The authentication token for the Autotel API.
        
        Returns:
            str: The ride comment if available, otherwise an empty string.
        """
        payload = {
            'Data': f'/{ride_id}',
            'Opcode': 'GetReservation',
            'Username': 'x',
            'Password': 'x'
        }
        try:
            data = await utils.fetch_data(url, self.x_token, payload)
            if not data or 'Data' not in data or not data.get('Data'):
                raise RuntimeError(f"No data received for ride ID: {ride_id}")
        except Exception:
            self.x_token = self.x_token_request(service_name)
            data = await utils.fetch_data(url, self.x_token, payload)
        if not data or 'Data' not in data or not data.get('Data'):
            return "No comment"
        
        return json.loads(data.get('Data', '{}')).get('comment', 'No comment')