from functools import partial
import os
from time import sleep
import settings
from services import WebAccess, TinyDatabase, QueryBuilder
from datetime import datetime as dt, timedelta
from src.pages import RidesPage, RidePage
from src.shared import utils
class LateAlert:
    def __init__(self, show_toast, gui_table_row, web_access: WebAccess, open_ride):
        self.show_toast = show_toast
        self.gui_table_row = gui_table_row
        self.web_access = web_access
        self.open_ride = open_ride
        
    def start_requests(self):
        late_rides = None
        
        for _ in range(settings.retry_count):
            self.web_access.create_new_page('goto_bo', f'{settings.goto_url}/index.html#/orders/current/', 'reuse')
            late_rides = self.fetch_late_ride()
            if late_rides:
                break
        
        if not late_rides:
            self.gui_table_row([['No late reservations found', '0', '0', '0']], btn_colors=("#1d5cd0", "#392890","#1f1f68"))
            return self._notify_no_late_reservations()
        
        self.rows = []
        for ride in late_rides:
            self._process_ride(ride)
        
        page = self.web_access.create_new_page('goto_bo', f'{settings.goto_url}/index.html#/orders/future/', 'reuse')
        for row in self.rows:
            car_license = row[2]
            RidesPage(page).search_by_car_license(car_license)
            sleep(2)
            for sorted_row in RidesPage(page).orders_table_rows:
                start_time = RidesPage(page).row_start_time_cell(sorted_row).text_content().strip()
                ride_id = RidesPage(page).get_ride_id_from_row(sorted_row).text_content().strip()
                if not row[3] or self._parse_time(start_time) < self._parse_time(row[3]):
                    row[2], row[3] = ride_id, start_time
            if row[3]:
                callback = partial(self.open_ride.emit, self._build_ride_url(row[2]))
                row[2] = (row[2], callback)
            else:
                row[2] = row[3] = "No future ride found"
                
                
        self.gui_table_row(self.rows, btn_colors=('#1d5cd0', '#392890','#1f1f68'))
        
        for row in self.rows:
            ride_id, end_time, _, future_ride_time = row
            if self._should_skip_due_to_end_time(end_time):
                continue
            self._notify_late_ride(ride_id[0], end_time, future_ride_time)

    def _notify_no_late_reservations(self):
        self.show_toast(
            'Goto ~ Late Alert!',
            'No late reservations found',
            icon=utils.resource_path(settings.app_icon)
        )

    def _process_ride(self, ride: tuple[str,str]):
        end_time, car_license = self._retrieve_ride_details(ride)
        url = self._build_ride_url(ride[0])
        open_ride_url = partial(self.open_ride.emit, url)
        self.rows.append([(ride[0], open_ride_url), end_time, car_license, ""])


    def _should_skip_due_to_end_time(self, end_time):
        if end_time:
            try:
                end_time_dt = self._parse_time(end_time)
                return end_time_dt <= dt.now() - timedelta(minutes=30)
            except Exception as e:
                pass
        return False

    def _retrieve_ride_details(self, ride: tuple[str, str]):
        ride_url = self._build_ride_url(ride[0])
        self._open_ride_page(ride_url)
        
        end_time = self.fetch_end_time(self.web_access.pages['goto_bo'])
        car_license = self._get_car_license(self.web_access.pages['goto_bo'])


        return end_time, car_license

    def _build_ride_url(self, ride):
        return f'{settings.goto_url}/index.html#/orders/{ride}/details'
    
    def _get_car_license(self, page):
        try:
            return RidePage(page).car_license.text_content()
        except Exception as e:
            return None
        
    def _open_ride_page(self, ride_url: str):
        # self.web_access.create_new_page("ride", str(settings.goto_url), open_mode="reuse")
        self.web_access.create_new_page("goto_bo", ride_url, open_mode="replace")
        return self.web_access.pages['goto_bo']

    def _parse_time(self, time_str: str, dt_format: str = "%d/%m/%Y %H:%M") -> dt | None:
        try:
            return dt.strptime(time_str, dt_format) if time_str else None
        except Exception as e:
            pass
        return None

    def _notify_late_ride(self, ride, end_time, future_ride_time):
        msg = f"Ride {ride} ended at {end_time}."
        msg += f"\nNext ride at {future_ride_time}" if future_ride_time else "\nNo future ride found."
        self.show_toast(
            "Goto ~ Late Alert!",
            msg,
            icon=utils.resource_path(settings.app_icon)
        )

    def fetch_end_time(self, page):
        sleep(5)
        return RidePage(page).ride_end_time.text_content()

    def fetch_start_time(self, page):
        sleep(5)
        return RidePage(page).ride_start_time.text_content()
    
    def fetch_late_ride(self):
        """
        This function checks for late reservations.
        :param web_access: WebAccess instance
        :return: List of late reservations
        """
        return RidesPage(self.web_access.pages['goto_bo']).get_late_rides()
        
    
