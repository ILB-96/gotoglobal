import asyncio
from functools import partial
import json
from typing import Any, Dict, List
from src.shared import utils, BaseAlert
from datetime import timedelta
from datetime import datetime as dt

class LongRides(BaseAlert):
    """
    Class to handle long rides in the Autotel system.
    This class is responsible for managing long rides, including
    their creation, updates, and any other related operations.
    """
    def __init__(self, show_toast, gui_table_row, pointer, open_ride, x_token_request):
        super().__init__(
            show_toast=show_toast,
            gui_table_row=gui_table_row,
            open_ride=open_ride,
            x_token_request=x_token_request
        )
        self.pointer = pointer

        
    async def start_requests(self, x_token: str):
        """
        Initiates the process of fetching and processing long rides.
        This method will create a new page for long rides and fetch
        the relevant data.
        """  
        self.x_token = x_token
        # for _ in range(3):
        rows = await self.collect_rides_information()

        if not rows:
            return self.gui_table_row([['No long rides', '0', '0', '0', '0']])
        
        self.gui_table_row(rows)

    
    async def collect_rides_information(self):
        url = 'https://autotelpublicapiprod.gototech.co/API/SEND'
        payload = {
            'Data': "",
            'Opcode': 'GetCurrentReservations',
            'Username': 'x',
            'Password': 'x'
        }
        try:
            if not self.x_token:
                self.x_token = self.x_token_request('autotel')
            print(f"fetching data with x_token: {self.x_token}")
            data = await utils.fetch_data(url, self.x_token, payload)
            if not data or 'Data' not in data or not data.get('Data') or data.get('Data') == '[]':
                raise RuntimeError("No data received from Autotel API")

        except Exception:
            self.x_token = self.x_token_request('autotel')

            data = await utils.fetch_data(url, self.x_token, payload)

        if not data or 'Data' not in data or not data.get('Data') or data.get('Data') == '[]':
            return

        data = json.loads(data.get('Data', '[]'))

        return await self.parse_rows(data)

    async def parse_rows(self, data: List[Dict]) -> List[List[Any]]:
        rows = []
        for ride in data:
            ride_id = str(ride.get('id', 'Unknown ID'))
            driver_name = ride.get('driverFirstName', '') + ' ' + ride.get('driverLastName', '')
            car_license = ride.get('carLicencePlate', '')
            location = self.pointer(car_license.replace('-', '')) if self.pointer else "Unknown Location"
            actual_start_date = utils.parse_time(ride.get('actualStartDate', ''))
            if actual_start_date is not None:
                duration = dt.now() - actual_start_date
            else:
                duration = timedelta(seconds=0)
            row = [ride_id, driver_name, duration, location, ""]
            if duration >= timedelta(hours=3):    
                url = f"https://prodautotelbo.gototech.co/index.html#/orders/{ride_id}/details"
                open_ride_url = partial(self.open_ride.emit, url) if self.open_ride else None
                row[0] = (ride_id, open_ride_url)
                comment = await self.get_ride_comment(ride_id)
                row[-1] = comment
                rows.append(row)
        
        return rows
    
    async def get_ride_comment(self, ride_id: str) -> str:
        """
        Fetches the ride comment from the Autotel API.
        
        Args:
            ride_id (str): The ID of the ride.
            x_token (str): The authentication token for the Autotel API.
        
        Returns:
            str: The ride comment if available, otherwise an empty string.
        """
        url = 'https://autotelpublicapiprod.gototech.co/API/SEND'
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
            self.x_token = self.x_token_request('autotel')
            data = await utils.fetch_data(url, self.x_token, payload)
        if not data or 'Data' not in data or not data.get('Data'):
            return "No comment"
        
        return json.loads(data.get('Data', '{}')).get('comment', 'No comment')
        