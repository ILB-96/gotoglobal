import asyncio
from functools import partial
from typing import Any, List
from services import AsyncWebAccess
import settings
from src.shared import utils
from src import pages
from datetime import timedelta

class LongRides:
    """
    Class to handle long rides in the Autotel system.
    This class is responsible for managing long rides, including
    their creation, updates, and any other related operations.
    """
    def __init__(self, show_toast, gui_table_row, web_access: AsyncWebAccess, pointer, open_ride):
        self.show_toast = show_toast
        self.gui_table_row = gui_table_row
        self.web_access = web_access
        self.pointer = pointer
        self.open_ride = open_ride

        
    async def start_requests(self):
        """
        Initiates the process of fetching and processing long rides.
        This method will create a new page for long rides and fetch
        the relevant data.
        """  
        print("Long rides started")

        rows = []
        for _ in range(3):
            
            await self.collect_rides_information(rows)
            if rows:
                break

        print(f"Collected {len(rows)} long rides")
        tasks = [asyncio.create_task(self.process_long_ride(i, row)) for i, row in enumerate(rows)]
        rows = await asyncio.gather(*tasks)
            
        
        self.gui_table_row(rows)
        
        await asyncio.gather(*(self.web_access.close_page(f'autotel_ride{i}') for i in range(len(rows))))

    async def process_long_ride(self, index, row):
        url = row[-1]
        ride_comment = await self.get_ride_comment(url, index)
        return row[:-1] + [ride_comment]

    @utils.async_retry(allow_falsy=True)
    async def init_ride_page(self, url, index):
        page = await self.web_access.create_new_page(f"autotel_ride{index}", settings.autotel_url, "reuse")

        if 'login' in page.url:
            await page.goto(settings.autotel_url, wait_until="networkidle")
            if url != settings.autotel_url:
                await page.goto(url, wait_until="networkidle")
        elif url != settings.autotel_url:
            await page.goto(url, wait_until="networkidle")
        if url not in page.url:
            raise RuntimeError(f"Failed to load the page: {url}. Current URL: {page.url}")
        return page

    async def collect_rides_information(self, rows: List[List[Any]]):
        try:
            page = await self.web_access.create_new_page("autotel_bo", f'{settings.autotel_url}/index.html#/orders/current', "reuse")
            await page.wait_for_timeout(1000)
            await page.evaluate("""
            () => {
                const elem = document.querySelector('.table-form');
                const scope = angular.element(elem).scope();
                scope.ordersCtrl.refreshTime = 0;
            }
        """)
            rides_page = pages.RidesPage(page)
            await rides_page.set_ride_duration_sort("desc")
            table_rows = await rides_page.orders_table_rows()
            for row in table_rows:
                duration = str(await rides_page.get_duration_from_row(row).text_content()).strip()
                parsed_duration = self.parse_duration(duration)

                if parsed_duration < timedelta(hours=3):
                    break
                    
                ride_id = str(await rides_page.get_ride_id_from_row(row).text_content()).strip()
                driver_name = str(await rides_page.get_driver_name_from_row(row).text_content()).strip()
                car_id = str(await rides_page.get_car_id_from_row(row).text_content()).strip()
                location = self.pointer(car_id.replace('-', '')) if self.pointer else "Unknown Location"
                
                url = f"https://prodautotelbo.gototech.co/index.html#/orders/{ride_id}/details"
                    
                
                open_ride_url = partial(self.open_ride.emit, url) if self.open_ride else None
                rows.append([(ride_id, open_ride_url), driver_name, duration, location, url])
        except Exception:
            return rows.clear()
    def parse_duration(self, duration: str) -> timedelta:
        """
        Parses the duration string into total seconds.
        
        Args:
            duration (str): The duration string in the format "HH:MM:SS".
        
        Returns:
            timedelta: The duration as a timedelta object.
        """
        try:
            if 'n/a' in duration:
                return timedelta(seconds=0)
            
            hours, minutes, seconds = map(int, duration.split(':'))
            return timedelta(hours=hours, minutes=minutes, seconds=seconds)
        except Exception:
            return timedelta(seconds=0)

    @utils.async_retry()
    async def get_ride_comment(self, url: str, index) -> str:
        """
        Fetches the ride comment from the ride details page.
        
        Args:
            url (str): The URL of the ride details page.
        
        Returns:
            str: The ride comment if available, otherwise an empty string.
        """
        page = await self.init_ride_page(url, index)
        await page.wait_for_timeout(2000)
        ride_comment = (await pages.RidePage(page).ride_comment.input_value()).strip()
        
        return ride_comment if ride_comment else "No comment"
        