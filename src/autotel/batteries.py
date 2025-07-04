from functools import partial
import settings
from services import AsyncWebAccess

from src.pages import CarsPage, RidePage

from src.shared import utils

class BatteriesAlert:
    def __init__(self, show_toast, gui_table_row, web_access: AsyncWebAccess, pointer, open_ride):
        self.show_toast = show_toast
        self.gui_table_row = gui_table_row
        self.web_access = web_access
        self.pointer = pointer
        self.open_ride = open_ride
        
    async def start_requests(self):
        autotel_cars_url = f'{settings.autotel_url}/index.html#/cars'
        page = await self.init_ride_page(autotel_cars_url)

        
        cars_page = CarsPage(page)
        await self.select_car_options(cars_page)
        
        rows = []
        for row in await cars_page.cars_table_rows():
            data = await self.extract_car_details(row)
            rows.append(data)
        
        for index, row in enumerate(rows):
            await self.process_car_data(index, row)
            
        self.gui_table_row(rows)

        for row in rows:
            _, car_license, car_battery, location, _ = row
            self.notify_battery_condition(car_license, car_battery, location) 
            
    @utils.async_retry(allow_falsy=True)
    async def init_ride_page(self, url):
        await self.web_access.create_new_page("autotel_bo1", url, "reuse")

        if 'login' in self.web_access.pages["autotel_bo1"].url:
            await self.web_access.create_new_page("autotel_bo1", settings.autotel_url, "reuse")
            if url != settings.autotel_url:
                await self.web_access.pages["autotel_bo1"].goto(url, wait_until="networkidle")
                
        return self.web_access.pages["autotel_bo1"]
    
    @utils.async_retry(allow_falsy=True)
    async def process_car_data(self, index, row):
        page = await self.init_ride_page(row[-1])
        await page.wait_for_timeout(2000)
        comment = str(await RidePage(page).ride_comment.input_value()).strip()
        row[-1] = comment if comment else "No Comment"
        
    @utils.async_retry(allow_falsy=False)
    async def extract_car_details(self, row):
        car_license = str(await row.locator('//*[contains(@ng-click, "carsTableCtrl.showCarDetails(row)")]').text_content()).strip()
        car_battery = str(await row.locator('td', has_text='%').text_content()).strip()
        active_ride = str(await row.locator("//*[contains(@ng-if, \"::$root.matchProject('ATL')||($root.matchProject('E2E'))\")][4]").text_content()).strip()
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
        elif is_very_low_battery:
            self.show_toast(
                    "Autotel ~ Batteries Alert!",
                    f"Electric Car {car_id} has low battery: {car_battery}",
                    icon=utils.resource_path(settings.autotel_icon)
                )
    @utils.async_retry(allow_falsy=True)
    async def select_car_options(self, cars_page: CarsPage):
        await self.web_access.pages['autotel_bo1'].wait_for_timeout(3000)
        await (await cars_page.car_status_select()).select_option("number:60")
        await self.web_access.pages['autotel_bo1'].wait_for_timeout(3000)
        await (await cars_page.car_category_select()).select_option("number:1")
        await self.web_access.pages['autotel_bo1'].wait_for_timeout(3000)

