from services import TinyDatabase, WebAccess
from services import Log
from src.shared import PointerLocation
from src.pages import RidesPage
from datetime import datetime as dt

class LongRides:
    """
    Class to handle long rides in the Autotel system.
    This class is responsible for managing long rides, including
    their creation, updates, and any other related operations.
    """

    def __init__(self, db: TinyDatabase, show_toast, gui_table_row, web_access: WebAccess, pointer: PointerLocation):
        self.db = db
        self.show_toast = show_toast
        self.gui_table_row = gui_table_row
        self.web_access = web_access
        self.pointer = pointer
    
    def start_requests(self):
        """
        Initiates the process of fetching and processing long rides.
        This method will create a new page for long rides and fetch
        the relevant data.
        """

        page = self.web_access.create_new_page("autotel_bo", 'https://prodautotelbo.gototech.co/index.html#/orders/current', "reuse")
        self.web_access.pages['pointer'].reload(wait_until='networkidle')
        
        prev_duration = None
        rides_page = RidesPage(page)
        
        rides_page.set_ride_duration_sort("asc")
        rows = []
        for row in rides_page.orders_table_rows:
            duration = rides_page.get_duration_from_row(row).inner_text().strip()
        
            curr_duration_parsed = dt.strptime(duration, "%H:%M:%S") if 'n/a' not in duration else None
            
            if not prev_duration or not curr_duration_parsed or dt.strptime(prev_duration, "%H:%M:%S") > curr_duration_parsed:
                break
            prev_duration = duration
            
            ride_id = rides_page.get_ride_id_from_row(row).inner_text().strip()
            driver_id = rides_page.get_driver_id_from_row(row).inner_text().strip()
            location = self.pointer.search_location(ride_id.replace('-', ''))
            
            rows.append([ride_id, driver_id, duration, location])
            
            Log.info(f"Long Ride: {ride_id} | Driver: {driver_id} | Duration: {duration} | Location: {location}")
        
        self.gui_table_row(rows)
