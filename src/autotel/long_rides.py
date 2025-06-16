from functools import partial
from time import sleep
from services import TinyDatabase, WebAccess
import settings
from src.shared import PointerLocation
from src import pages
from datetime import timedelta

class LongRides:
    """
    Class to handle long rides in the Autotel system.
    This class is responsible for managing long rides, including
    their creation, updates, and any other related operations.
    """

    def __init__(self, show_toast, gui_table_row, web_access: WebAccess, pointer: PointerLocation | None, open_ride):
        self.show_toast = show_toast
        self.gui_table_row = gui_table_row
        self.web_access = web_access
        self.pointer = pointer
        self.open_ride = open_ride
        
    def start_requests(self):
        """
        Initiates the process of fetching and processing long rides.
        This method will create a new page for long rides and fetch
        the relevant data.
        """

        page = self.web_access.create_new_page("autotel_bo", f'{settings.autotel_url}/index.html#/orders/current', "reuse")
        self.web_access.create_new_page("autotel_ride", settings.autotel_url, "reuse")
        self.web_access.pages['pointer'].reload(wait_until='networkidle')
        
        rides_page = pages.RidesPage(page)
        
        rides_page.set_ride_duration_sort("asc")
        rows = []
        for row in rides_page.orders_table_rows:
            duration = rides_page.get_duration_from_row(row).inner_text().strip()
            parsed_duration = self.parse_duration(duration)

            if parsed_duration < timedelta(hours=3):
                break
            
            ride_id = rides_page.get_ride_id_from_row(row).inner_text().strip()
            driver_id = rides_page.get_driver_id_from_row(row).inner_text().strip()
            car_id = rides_page.get_car_id_from_row(row).inner_text().strip()
            location = self.pointer.search_location(car_id.replace('-', '')) if self.pointer else "Unknown Location"
            
            url = f"https://prodautotelbo.gototech.co/index.html#/orders/{ride_id}/details"
            
            
            open_ride_url = partial(self.open_ride.emit, url) if self.open_ride else None
            rows.append([(ride_id, open_ride_url), driver_id, duration, location, url])
        
        
        for row in rows:
            url = row[-1]
            ride_comment = self.get_ride_comment(url)
            row[-1] = ride_comment
            
        
        self.gui_table_row(rows)
    
    def parse_duration(self, duration: str) -> timedelta:
        """
        Parses the duration string into total seconds.
        
        Args:
            duration (str): The duration string in the format "HH:MM:SS".
        
        Returns:
            timedelta: The duration as a timedelta object.
        """
        if 'n/a' in duration:
            return timedelta(seconds=0)
        
        hours, minutes, seconds = map(int, duration.split(':'))
        return timedelta(hours=hours, minutes=minutes, seconds=seconds)
    
    def get_ride_comment(self, url: str) -> str:
        """
        Fetches the ride comment from the ride details page.
        
        Args:
            url (str): The URL of the ride details page.
        
        Returns:
            str: The ride comment if available, otherwise an empty string.
        """
        page = self.web_access.create_new_page("autotel_ride", url, "reuse", wait_until='domcontentloaded')
        sleep(1)
        ride_comment = pages.RidePage(page).ride_comment.input_value().strip()
        
        return ride_comment if ride_comment else "No comment"
        