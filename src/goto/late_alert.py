from functools import partial
import json
import settings

from datetime import datetime as dt, timedelta
from src.shared import utils
from src.shared import BaseAlert
class LateAlert(BaseAlert):
    def __init__(self, show_toast, gui_table_row, open_ride, x_token_request):
        super().__init__(show_toast, gui_table_row, open_ride, x_token_request)
        self.recently_notified = {}
        
    async def start_requests(self, x_token):
        self.x_token = x_token
        
        late_rides = await self.fetch_late_rides()
        
        if not late_rides or late_rides == "No result":
            return self.gui_table_row([['No late rides', '0', '0', '0', '0']])
        
        self.gui_table_row(late_rides)
        
        self.notify_late_ride_endings(late_rides)

    def notify_late_ride_endings(self, late_rides):
        now = dt.now()
        cutoff = now - timedelta(minutes=30)

        # Clean old entries
        self.recently_notified = {
            k: v for k, v in self.recently_notified.items() if v > cutoff
        }

        for row in late_rides:
            ride_id = row[0][0] if isinstance(row[0], tuple) else row[0]
            end_time = dt.strptime(row[1], "%d/%m/%Y %H:%M")

            # Only notify if ended in the last 30 min
            if end_time < cutoff or end_time > now:
                continue

            # Only notify once every 15 minutes
            last_notified = self.recently_notified.get(ride_id)
            if last_notified and now - last_notified < timedelta(minutes=15):
                continue

            self.recently_notified[ride_id] = now  # Update last notified
            self.show_toast(
                'Goto ~ Late Alert!',
                f"Ride {ride_id} ended at {row[1]}. Next ride at {row[3]}",
                icon=utils.resource_path(settings.app_icon)
            )
            
    @utils.async_retry()
    async def fetch_late_rides(self):
        """
        This function checks for late reservations.
        :param x_token: X-Token for authentication
        :return: List of late reservations
        """
        url = 'https://car2gopublicapi.gototech.co/API/SEND'
        payload = {
            "Opcode": "getCurrentReservations",
            "Data": "",
            "username": "x",
            "password": "x"
        }
        try:
            if not self.x_token:
                self.x_token = self.x_token_request('goto')
            data = await utils.fetch_data(url, self.x_token, payload)
            if not data or not data.get('Data'):
                print('No data found for late rides:', data)
                raise ValueError("No data found for late rides")
        except Exception as e:
            print('Error fetching late rides:', e)
            self.x_token = self.x_token_request('goto')
            if not self.x_token:
                raise RuntimeError("Failed to fetch X-Token for Goto")
            data = await utils.fetch_data(url, self.x_token, payload)

        if not data or not data.get('Data') or data.get('Data') == '[]':
            raise ValueError("No data found for late rides")
        parsed_data = json.loads(data.get('Data', '[]'))
        # print(parsed_data)
        return await self.get_late_rides(parsed_data)
    
    async def get_late_rides(self, data):
        """
        This function processes the fetched data to find late rides.
        :param data: Fetched data from the API
        :return: List of late rides
        """
        # print("Type of data:", type(data))
        

        rows = []
        for ride in data:
            # print('Processing ride:', ride)
            if not (endDate := ride.get('endDate')):
                print('No endDate found for ride:', ride)
                continue
            parsed_end_date = utils.parse_time(endDate)
            car_license = ride.get('carLicencePlate')
            ride_id = ride.get('id', 'No ride ID found')            
            
           
            
            if parsed_end_date and parsed_end_date <= dt.now():
                url = self.build_ride_url(ride_id, settings.goto_url)
                open_ride_url = partial(self.open_ride.emit, url) if self.open_ride else None
                comment = await self.get_ride_comment(ride_id, 'goto', 'https://car2gopublicapi.gototech.co/API/SEND')
                future_ride_id, future_ride_time = await self.get_future_ride_info(car_license)

                row = [(ride_id, open_ride_url), parsed_end_date.strftime("%d/%m/%Y %H:%M"), future_ride_id, future_ride_time, comment]
                rows.append(row)

                
        return rows
    async def get_future_ride_info(self, car_license: str):
        """
        Fetches the future ride information based on the car license.
        :param car_license: The license plate of the car
        :return: Tuple containing future ride ID and time
        """
        if not car_license or car_license == "No result":
            return "No car license found", "No future ride found"
        
        url = 'https://car2gopublicapi.gototech.co/API/SEND'
        payload = {
            "Username": "x",
            "Password": "x",
            "Opcode": "GetFutureReservations",
            "Data": ""
        }
        
        try:
            data = await utils.fetch_data(url, self.x_token, payload)
            if not data or not data.get('Data'):
                raise ValueError("No data found for future ride info")
        except Exception as e:
            self.x_token = self.x_token_request('goto')

            data = await utils.fetch_data(url, self.x_token, payload)

        parsed_data = json.loads(data.get('Data', '[]'))
        if not parsed_data:
            return "No future ride", "No future ride"
        
        future_ride_id = None
        future_ride_date = None
        for ride in parsed_data:
            if ride.get('carLicencePlate') != car_license:
                continue
            id = ride.get('id')
            parsed_date = utils.parse_time(ride.get('startDate'), "%Y-%m-%dT%H:%M:%S")
            if parsed_date and (not future_ride_date or parsed_date < future_ride_date):
                future_ride_id = id
                future_ride_date = parsed_date

        return (future_ride_id, future_ride_date.strftime("%d/%m/%Y %H:%M")) if future_ride_date else ("No future ride", "No future ride")
