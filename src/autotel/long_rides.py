from functools import partial
from typing import Any, List
from services import WebAccess
import settings
from src.shared import PointerLocation, utils
from src import pages
from datetime import timedelta

class LongRides:
    """
    Class to handle long rides in the Autotel system.
    This class is responsible for managing long rides, including
    their creation, updates, and any other related operations.
    """
    def __init__(self, show_toast, gui_table_row, web_access: WebAccess, pointer, open_ride):
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
        self.init_ride_page(settings.autotel_url)        
        
        rows = []
        for _ in range(3):
            self.collect_rides_information(rows)
            if rows:
                break
        
        for row in rows:
            url = row[-1]
            ride_comment = self.get_ride_comment(url)
            row[-1] = ride_comment
            
        
        self.gui_table_row(rows)

    utils.retry(allow_falsy=True)
    def init_ride_page(self, url):
        self.web_access.create_new_page("autotel_ride", url, "reuse")

        if 'login' in self.web_access.pages["autotel_ride"].url:
            self.web_access.create_new_page("autotel_ride", url, "reuse")
            if url != settings.autotel_url:
                self.web_access.pages["autotel_ride"].goto(url, wait_until="networkidle")
        return self.web_access.pages["autotel_ride"]

    def collect_rides_information(self, rows: List[List[Any]]):
        try:
            page = self.web_access.create_new_page("autotel_bo", f'{settings.autotel_url}/index.html#/orders/current', "reuse")
            page.wait_for_timeout(1000)
            rides_page = pages.RidesPage(page)
            rides_page.set_ride_duration_sort("desc")
            page.evaluate("""
                            const observer = new MutationObserver(() => {});
                            observer.observe(document, { childList: true, subtree: true });
                            window.setInterval = () => {};
                            window.setTimeout = () => {};
                            window.requestAnimationFrame = () => {};
                          """)
            table_rows = rides_page.orders_table_rows
            for row in table_rows:
                duration = rides_page.get_duration_from_row(row).inner_text().strip()
                parsed_duration = self.parse_duration(duration)

                if parsed_duration < timedelta(hours=3):
                    break
                    
                ride_id = rides_page.get_ride_id_from_row(row).inner_text().strip()
                driver_name = rides_page.get_driver_name_from_row(row).inner_text().strip()
                car_id = rides_page.get_car_id_from_row(row).inner_text().strip()
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
    utils.retry()
    def get_ride_comment(self, url: str) -> str:
        """
        Fetches the ride comment from the ride details page.
        
        Args:
            url (str): The URL of the ride details page.
        
        Returns:
            str: The ride comment if available, otherwise an empty string.
        """
        page = self.init_ride_page(url)
        page.wait_for_timeout(2000)
        ride_comment = pages.RidePage(page).ride_comment.input_value().strip()
        
        return ride_comment if ride_comment else "No comment"
        