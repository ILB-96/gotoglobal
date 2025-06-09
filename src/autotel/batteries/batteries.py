import os
from time import sleep
import settings
from services import WebAccess, TinyDatabase
from datetime import datetime as dt

from src.pages import CarsPage
from src.shared import PointerLocation

class BatteriesAlert:
    def __init__(self, db:TinyDatabase, show_toast, gui_table_row, web_access: WebAccess, pointer: PointerLocation | None):
        self.db = db
        self.show_toast = show_toast
        self.gui_table_row = gui_table_row
        self.web_access = web_access
        self.pointer = pointer
        
    def start_requests(self):
        autotel_cars_url = r'https://prodautotelbo.gototech.co/index.html#/cars'
        page = self.web_access.create_new_page("autotel_bo", autotel_cars_url, "update")
        
        cars_page = CarsPage(page)
        self.select_car_options(cars_page)
        
        rows = []
        for row in cars_page.cars_table_rows:
            data = self.extract_car_details(row)
            rows.append(data)
            
        self.gui_table_row(rows)

        for row in rows:
            active_ride, car_id, car_battery, location = row
            if self.db.find_one({'ride_id': active_ride}, 'autotel'):
                continue
            
            self.db.upsert_one(
                {'ride_id': active_ride, 
                'car_id': car_id, 
                'car_battery': car_battery, 
                'location': location, 
                'report_time': dt.now().strftime("%d/%m/%Y %H:%M")
                },
                'autotel'
            )

            self.notify_battery_condition(car_id, car_battery, location)

    def extract_car_details(self, row):
        car_id = str(row.locator('//*[contains(@ng-click, "carsTableCtrl.showCarDetails(row)")]').text_content()).strip()
        car_battery = str(row.locator('td', has_text='%').text_content()).strip()
        active_ride = str(row.locator("//*[contains(@ng-if, \"::$root.matchProject('ATL')||($root.matchProject('E2E'))\")][4]").text_content()).strip()
        location = self.pointer.search_location(car_id.replace("-", "")) if self.pointer else "Unknown Location"
        
        return [active_ride, car_id, car_battery, location]

    def notify_battery_condition(self, car_id, car_battery, location):
        is_low_battery = int(car_battery.replace("%", "")) <= 30
        is_not_service_location ='תל אביב' not in location
                                      
        if is_low_battery and is_not_service_location:
            self.show_toast(
                    "Autotel ~ Batteries Alert!",
                    f"Electric Car {car_id} has low battery: {car_battery} Outside of Tel Aviv",
                    icon=os.path.abspath(settings.app_icon)
                )
        elif is_not_service_location:
            self.show_toast(
                    "Autotel ~ Batteries Alert!",
                    f"Electric Car {car_id}\nwith {car_battery} battery\nis not in Tel Aviv: {location}",
                    icon=os.path.abspath(settings.app_icon)
                )
        elif is_low_battery:
            self.show_toast(
                    "Autotel ~ Batteries Alert!",
                    f"Electric Car {car_id} has low battery: {car_battery}",
                    icon=os.path.abspath(settings.app_icon)
                )

    def select_car_options(self, cars_page: CarsPage):
        sleep(3)
        cars_page.car_status_select.select_option("number:60")
        sleep(3)
        cars_page.car_category_select.select_option("number:1")
        sleep(3)

