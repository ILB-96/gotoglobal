import asyncio
from functools import partial
import json
from typing import Any, Dict, List
import settings
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
            x_token_request=x_token_request,
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

    @utils.async_retry(allow_falsy=True)
    async def collect_rides_information(self):
        url = 'https://autotelpublicapiprod.gototech.co/API/SEND'
        payload = {
            'Data': "",
            'Opcode': 'GetCurrentReservations',
            'Username': 'x',
            'Password': 'x'
        }
        data = await self.fetch_data_from_api(url, payload)

        if not data or 'Data' not in data or not data.get('Data') or data.get('Data') == '[]':
            return

        data = json.loads(data.get('Data', '[]'))

        return await self.parse_rows(data)

    async def fetch_data_from_api(self, url, payload):
        try:
            if not self.x_token:
                self.x_token = self.x_token_request('autotel')
            data = await utils.fetch_data(url, self.x_token, payload)
            if not data or 'Data' not in data or not data.get('Data') or data.get('Data') == '[]':
                raise RuntimeError("No data received from Autotel API")

        except Exception:
            self.x_token = self.x_token_request('autotel')

            data = await utils.fetch_data(url, self.x_token, payload)
        return data

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
                url = self.build_ride_url(ride_id, settings.autotel_url)
                open_ride_url = partial(self.open_ride.emit, url) if self.open_ride else None
                row[0] = (ride_id, open_ride_url)
                comment = await self.get_ride_comment(ride_id, 'autotel', 'https://autotelpublicapiprod.gototech.co/API/SEND')
                row[-1] = comment
                rows.append(row)
        
        return rows
        