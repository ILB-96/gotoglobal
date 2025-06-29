from functools import partial
import settings
from services import WebAccess

from src.pages import CarsPage
from src.pages.ride_page import RidePage
from src.shared import PointerLocation, utils

class BatteriesAlert:
    def __init__(self, show_toast, gui_table_row, web_access: WebAccess, pointer, open_ride):
        self.show_toast = show_toast
        self.gui_table_row = gui_table_row
        self.web_access = web_access
        self.pointer = pointer
        self.open_ride = open_ride
        
    def start_requests(self):
        autotel_cars_url = f'{settings.autotel_url}/index.html#/cars'
        page = self.web_access.create_new_page("autotel_bo", autotel_cars_url, "reuse")
        
        cars_page = CarsPage(page)
        self.select_car_options(cars_page)
        
        rows = []
        for row in cars_page.cars_table_rows:
            data = self.extract_car_details(row)
            rows.append(data)
        
        for row in rows:
            self.process_car_data(row)
            
        self.gui_table_row(rows)

        for row in rows:
            _, car_license, car_battery, location, _ = row
            self.notify_battery_condition(car_license, car_battery, location)

    @utils.retry(allow_falsy=True)
    def process_car_data(self, row):
        page = self.web_access.create_new_page('autotel_bo', row[-1], 'reuse')
        if 'login' in page.url:
            self.web_access.create_new_page('autotel_bo', settings.autotel_url)
            page = self.web_access.create_new_page('autotel_bo', row[-1], 'reuse')
        page.wait_for_timeout(2000)
        row[-1] = RidePage(page).ride_comment.input_value().strip()
        
    @utils.retry(allow_falsy=False)
    def extract_car_details(self, row):
        car_license = str(row.locator('//*[contains(@ng-click, "carsTableCtrl.showCarDetails(row)")]').text_content()).strip()
        car_battery = str(row.locator('td', has_text='%').text_content()).strip()
        active_ride = str(row.locator("//*[contains(@ng-if, \"::$root.matchProject('ATL')||($root.matchProject('E2E'))\")][4]").text_content()).strip()
        location = self.pointer(car_license.replace('-', '')) if self.pointer else "Unknown Location"
        url = f"{settings.autotel_url}/index.html#/orders/{active_ride}/details"
        open_ride_url = partial(self.open_ride.emit, url) if self.open_ride else None
        return [(active_ride, open_ride_url), car_license, car_battery, location, url]

    def notify_battery_condition(self, car_id, car_battery, location):
        is_low_battery = int(car_battery.replace("%", "")) <= 30
        is_very_low_battery = int(car_battery.replace("%", "")) <= 15
        is_not_service_location ='תל אביב' not in location
                                      
        if is_low_battery and is_not_service_location:
            self.show_toast(
                    "Autotel ~ Batteries Alert!",
                    f"Electric Car {car_id} has low battery: {car_battery} Outside of Tel Aviv",
                    icon=utils.resource_path(settings.autotel_icon)
                )
        # elif is_not_service_location:
        #     self.show_toast(
        #             "Autotel ~ Batteries Alert!",
        #             f"Electric Car {car_id}\nwith {car_battery} battery\nis not in Tel Aviv: {location}",
        #             icon=utils.resource_path(settings.autotel_icon)
        # )
        elif is_very_low_battery:
            self.show_toast(
                    "Autotel ~ Batteries Alert!",
                    f"Electric Car {car_id} has low battery: {car_battery}",
                    icon=utils.resource_path(settings.autotel_icon)
                )
    @utils.retry(allow_falsy=True)
    def select_car_options(self, cars_page: CarsPage):
        self.web_access.pages['autotel_bo'].wait_for_timeout(3000)
        cars_page.car_status_select.select_option("number:60")
        self.web_access.pages['autotel_bo'].wait_for_timeout(3000)
        cars_page.car_category_select.select_option("number:1")
        self.web_access.pages['autotel_bo'].wait_for_timeout(3000)

