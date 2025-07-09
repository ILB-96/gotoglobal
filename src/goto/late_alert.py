import asyncio
from functools import partial
import json
import settings
from services import AsyncWebAccess
from datetime import datetime as dt, timedelta
from src.pages import RidesPage, RidePage
from src.shared import utils
from src.shared import BaseAlert
class LateAlert(BaseAlert):
    def __init__(self, show_toast, gui_table_row, open_ride, x_token_request):

        super().__init__(show_toast, gui_table_row, open_ride, x_token_request)
        
    async def start_requests(self, x_token):
        self.x_token = x_token
        late_rides = None
        
        late_rides = await self.fetch_late_rides()
        
        if not late_rides or late_rides == "No result":
            self.gui_table_row([['No late rides', '0', '0', '0', '0']])
            return self._notify_no_late_reservations()
        
    async def fetch_late_rides(self):
        """
        This function checks for late reservations.
        :param x_token: X-Token for authentication
        :return: List of late reservations
        """
        print('Fetching late rides...')
        if self.x_token is None:
            self.x_token = self.x_token_request('goto')
        print('Fetching late rides with x_token:', self.x_token)
        url = 'https://car2gopublicapi.gototech.co/API/SEND'
        payload = {
            "Opcode": "getCurrentReservations",
            "Data": "",
            "username": "x",
            "password": "x"
        }
        try:
            data = await utils.fetch_data(url, self.x_token, payload)
            if not data or not data.get('Data'):
                print('No data found for late rides:', data)
                raise ValueError("No data found for late rides")
        except Exception as e:
            print('Error fetching late rides:', e)
            self.x_token = self.x_token_request('goto')
            if not self.x_token:
                return
            data = await utils.fetch_data(url, self.x_token, payload)
        # print(data)
        if not data or not data.get('Data'):
            return
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
        

        late_rides = []
        for ride in data:
            # print('Processing ride:', ride)
            if not ride.get('endDate'):
                print('No endDate found for ride:', ride)
                continue
            parsed_end_date = utils.parse_time(ride['endDate'])
            car_license = ride.get('carLicencePlate')
            ride_id = ride.get('id', 'No ride ID found')            
            
           
            row = [ride_id, parsed_end_date, "", "", ""]
            if parsed_end_date and parsed_end_date <= dt.now():
                comment = await self.get_ride_comment(ride_id)
                future_ride_id, future_ride_time = self.get_future_ride_info(car_license)
                row[3] = future_ride_id
                row[4] = future_ride_time
                row[5] = comment
                late_rides.append(row)
            # print(row)
                
        return late_rides
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
            if not self.x_token:
                self.x_token = self.x_token_request('goto')

            data = await utils.fetch_data(url, self.x_token, payload)
            if not data or not data.get('Data'):
                raise ValueError("No data found for future ride info")
        except Exception as e:
            if not self.x_token:
                self.x_token = self.x_token_request('goto')

            data = await utils.fetch_data(url, self.x_token, payload)

        parsed_data = json.loads(data.get('Data', '[]'))
        if not parsed_data:
            return "No future ride found", ""
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

        return future_ride_id, future_ride_date.strftime("%d/%m/%Y %H:%M") if future_ride_date else "No future ride found"
    async def get_ride_comment(self, ride_id: str) -> str:
        """
        Fetches the ride comment for a given ride ID.
        :param ride_id: The ID of the ride
        :return: The comment for the ride
        """
        url = 'https://car2gopublicapi.gototech.co/API/SEND'
        payload = {
                "Username": "x",
                "Password": "x",
                "Opcode": "GetReservation",
                "Data": f"/{ride_id}"
        }
        try:
            if not self.x_token:
                self.x_token = self.x_token_request('goto')

            data = await utils.fetch_data(url, self.x_token, payload)
            if not data or not data.get('Data') or data.get('Data') == '{}':
                raise ValueError("No data found for ride comment")
        except Exception as e:
            if not self.x_token:
                self.x_token = self.x_token_request('goto')

            data = await utils.fetch_data(url, self.x_token, payload)

        return json.loads(data.get('Data', '{}')).get('comment', 'No comment found')


    #     print('Late rides found:', late_rides)
    #     tasks = [asyncio.create_task(self._process_ride(ride)) for ride in late_rides]
    #     rows = await asyncio.gather(*tasks)
        
    #     page = await self.create_future_orders_page()
    #     for row in rows:
    #         await self.fetch_future_ride(page, row)
                
                
    #     self.gui_table_row(rows)
        
    #     self.notify_late_rides(rows)
        
    # @utils.async_retry()
    # async def fetch_late_rides(self):
    #     await self.init_page('goto_bo', settings.goto_url, settings.goto_url, timeout=2000)
    #     return await self.fetch_late_ride()

    
    # async def fetch_late_ride(self):
    #     """
    #     This function checks for late reservations.
    #     :param web_access: WebAccess instance
    #     :return: List of late reservations
    #     """
    #     return await RidesPage(self.web_access.pages['goto_bo']).get_late_rides()
    
    # @utils.async_retry(allow_falsy=True)
    # async def fetch_future_ride(self, page, row):
    #     car_license = row[2]
    #     if not car_license or car_license == "No result":
    #         row[2] = row[3] = "No car license found"
    #         return
    #     await RidesPage(page).search_by_car_license(car_license)
    #     await page.wait_for_timeout(2000)
    #     for sorted_row in await RidesPage(page).orders_table_rows():
    #         start_time = await self.fetch_row_start_time(page, sorted_row)
    #         ride_id = await self.fetch_row_ride_id(page, sorted_row)
    #         parsed_start_time = self._parse_time(start_time)
    #         parsed_row_time = self._parse_time(row[3])
    #         if not row[3] or (parsed_start_time is not None and parsed_row_time is not None and parsed_start_time < parsed_row_time):
    #             row[2], row[3] = ride_id, start_time
    #     if row[3]:
    #         callback = partial(self.open_ride.emit, self.build_ride_url(row[2], settings.goto_url))
    #         row[2] = (row[2], callback)
    #     else:
    #         row[2] = row[3] = "No future ride found"

    # @utils.async_retry()
    # async def fetch_row_ride_id(self, page, sorted_row):
    #     return str(await RidesPage(page).get_ride_id_from_row(sorted_row).text_content()).strip()

    # @utils.async_retry()
    # async def fetch_row_start_time(self, page, sorted_row):
    #     return str(await RidesPage(page).row_start_time_cell(sorted_row).text_content()).strip()

    # @utils.async_retry()
    # async def create_future_orders_page(self):
    #     page = await self.init_page('goto_bo', f'{settings.goto_url}/index.html#/orders/future/', settings.goto_url, timeout=1000)
    #     return page

    # def notify_late_rides(self, rows):
    #     for row in rows:
    #         ride_id, end_time, _, future_ride_time, _ = row
    #         if self._should_skip_due_to_end_time(end_time):
    #             continue
    #         self._notify_late_ride(ride_id[0], end_time, future_ride_time)


    def _notify_no_late_reservations(self):
        self.show_toast(
            'Goto ~ Late Alert!',
            'No late reservations found',
            icon=utils.resource_path(settings.app_icon)
        )

    # async def _process_ride(self, ride: str):
    #     page = await self._init_ride_page(ride)
    #     print(f"Processing ride: {ride}")
                
    #     end_time = await self._fetch_end_time(page)
    #     car_license = await self._get_car_license(page)
    #     ride_comment = await self._get_ride_comment(page)
    #     await self.web_access.close_page(f'goto_ride{ride}')
    #     url = self.build_ride_url(ride, settings.goto_url)
    #     open_ride_url = partial(self.open_ride.emit, url)
    #     return [(ride, open_ride_url), end_time, car_license, "", ride_comment]


    # def _should_skip_due_to_end_time(self, end_time):
    #     if end_time:
    #         try:
    #             end_time_dt = self._parse_time(end_time)
    #             return end_time_dt and end_time_dt <= dt.now() - timedelta(minutes=30)
    #         except Exception:
    #             return False
    
    # @utils.async_retry()
    # async def _init_ride_page(self, ride: str):
    #     ride_url = self.build_ride_url(ride, settings.goto_url)
    #     print(f"Initializing ride page for ride: {ride} with URL: {ride_url}")
    #     return await self.init_page(f'goto_ride{ride}', ride_url, settings.goto_url, 1000)
    
    # @utils.async_retry(allow_falsy=True)
    # async def _get_ride_comment(self, page):
    #     try:
    #         return (await RidePage(page).ride_comment.input_value()).strip()
    #     except Exception:
    #         return None
    
    # @utils.async_retry()
    # async def _get_car_license(self, page):
    #     try:
    #         return str(await RidePage(page).car_license.text_content()).strip()
    #     except Exception:
    #         return None
    
    # @utils.async_retry()
    # async def _open_ride_page(self, ride, ride_url: str):
    #     page = await self.web_access.create_new_page(f"goto_ride{ride}", ride_url, open_mode="reuse")
    #     if 'login' in page.url:
    #         await page.goto(settings.goto_url, wait_until="networkidle")
    #         if ride_url != settings.goto_url:
    #             await page.goto(ride_url, wait_until="networkidle")
    #     return page

    # def _parse_time(self, time_str: str, dt_format: str = "%d/%m/%Y %H:%M") -> dt | None:
    #     try:
    #         return dt.strptime(time_str, dt_format) if time_str else None
    #     except Exception as e:
    #         return None

    # def _notify_late_ride(self, ride, end_time, future_ride_time):
    #     msg = f"Ride {ride} ended at {end_time}."
    #     msg += f"\nNext ride at {future_ride_time}" if future_ride_time else "\nNo future ride found."
    #     self.show_toast(
    #         "Goto ~ Late Alert!",
    #         msg,
    #         icon=utils.resource_path(settings.app_icon)
    #     )
    
    # @utils.async_retry()
    # async def _fetch_end_time(self, page):
    #     await page.wait_for_timeout(1000)
    #     element = RidePage(page).ride_end_time
    #     content = await element.text_content()
    #     return str(content).strip()


