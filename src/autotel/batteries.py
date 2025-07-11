from functools import partial
import json
import settings

from src.shared import utils
from src.shared import BaseAlert

class BatteriesAlert(BaseAlert):
    def __init__(self, show_toast, gui_table_row, pointer, open_ride, x_token_request):
        super().__init__(
            show_toast=show_toast,
            gui_table_row=gui_table_row,
            open_ride=open_ride,
            x_token_request=x_token_request,
        )
        self.pointer = pointer
        
    async def start_requests(self, x_token: str):
        self.x_token = x_token
        
        
        rows = await self.get_batteries_data()
        
        if not rows:
            return self.gui_table_row([['No batteries rides', '0', '0', '0', '0']])
        
        self.gui_table_row(rows)
        
        for row in rows:
            if float(row[2].strip('%')) <= 30 and 'תל אביב' not in row[3]:
                self.show_toast(
                    'Autotel - Battery Alert!',
                    f"Low battery for ride {row[0]}: {row[2]}",
                    icon=utils.resource_path(settings.autotel_icon)
                )
        
    async def get_batteries_data(self):
        url = 'https://autotelpublicapiprod.gototech.co/API/SEND/GetAllCars'
        payload = {
            'Data': 'null/null/1/false',
            'Opcode': 'GetAllCars',
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
        data = json.loads(data.get('Data'))
        return await self.process_batteries_data(data)
    
    async def process_batteries_data(self, data):
        rows = []
        for car in data:
            ride_id = car.get('activeReservationNum')
            category = car.get('categoryId')
            if not ride_id or not category or category != 1:
                continue
            license_plate = car.get('licencePlate', '')
            battery = str(car.get('lastFuelPercentage', 0)) + '%'
            location = self.pointer(license_plate.replace('-', ''))
            
            url = self.build_ride_url(ride_id, settings.autotel_url)
            open_ride_url = partial(self.open_ride.emit, url) if self.open_ride else None
            
            comment = await self.get_ride_comment(ride_id, 'autotel', 'https://autotelpublicapiprod.gototech.co/API/SEND')
            row = [(ride_id, open_ride_url), license_plate, battery, location, comment]
            rows.append(row)
            
        
        return rows
    
        