from functools import partial
import settings
from services import WebAccess
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
        
        late_rides = self.fetch_late_rides()
        
        if not late_rides or late_rides == "No result":
            self.gui_table_row([['No late rides', '0', '0', '0', '0']])
            return self._notify_no_late_reservations()
        
        rows = []
        for ride in late_rides:
            self._process_ride(rows, ride)
        
        page = self.create_future_orders_page()
        for row in rows:
            self.fetch_future_ride(page, row)
                
                
        self.gui_table_row(rows)
        
        self.notify_late_rides(rows)
    @utils.retry()
    def fetch_late_rides(self):
        self.web_access.create_new_page('goto_bo', f'{settings.goto_url}/index.html#/orders/current/', 'reuse')
        self.web_access.pages['goto_bo'].wait_for_timeout(3000)
        result = self.fetch_late_ride()
        print(result)
        return result
    
    def fetch_late_ride(self):
        """
        This function checks for late reservations.
        :param web_access: WebAccess instance
        :return: List of late reservations
        """
        result = RidesPage(self.web_access.pages['goto_bo']).get_late_rides()
        print(f"Late rides fetched: {result}")
        return result
    
    @utils.retry(allow_falsy=True)
    def fetch_future_ride(self, page, row):
        car_license = row[2]
        if not car_license or car_license == "No result":
            row[2] = row[3] = "No car license found"
            return
        RidesPage(page).search_by_car_license(car_license)
        page.wait_for_timeout(2000)
        for sorted_row in RidesPage(page).orders_table_rows:
            start_time = self.fetch_row_start_time(page, sorted_row)
            ride_id = self.fetch_row_ride_id(page, sorted_row)
            parsed_start_time = self._parse_time(start_time)
            parsed_row_time = self._parse_time(row[3])
            if not row[3] or (parsed_start_time is not None and parsed_row_time is not None and parsed_start_time < parsed_row_time):
                row[2], row[3] = ride_id, start_time
        if row[3]:
            callback = partial(self.open_ride.emit, self._build_ride_url(row[2]))
            row[2] = (row[2], callback)
        else:
            row[2] = row[3] = "No future ride found"

    @utils.retry()
    def fetch_row_ride_id(self, page, sorted_row):
        return RidesPage(page).get_ride_id_from_row(sorted_row).text_content().strip()
    
    @utils.retry()
    def fetch_row_start_time(self, page, sorted_row):
        return RidesPage(page).row_start_time_cell(sorted_row).text_content().strip()

    @utils.retry(allow_falsy=True)
    def create_future_orders_page(self):
        page = self.web_access.create_new_page('goto_bo', f'{settings.goto_url}/index.html#/orders/future/', 'reuse')
        return page

    def notify_late_rides(self, rows):
        for row in rows:
            ride_id, end_time, _, future_ride_time, _ = row
            if self._should_skip_due_to_end_time(end_time):
                continue
            self._notify_late_ride(ride_id[0], end_time, future_ride_time)


    def _notify_no_late_reservations(self):
        self.show_toast(
            'Goto ~ Late Alert!',
            'No late reservations found',
            icon=utils.resource_path(settings.app_icon)
        )

    def _process_ride(self, rows, ride: str):
        self._retrieve_ride_details(ride)
                
        end_time = self.fetch_end_time(self.web_access.pages['goto_bo'])
        car_license = self._get_car_license(self.web_access.pages['goto_bo'])
        ride_comment = self._get_ride_comment(self.web_access.pages['goto_bo'])
        
        url = self._build_ride_url(ride)
        open_ride_url = partial(self.open_ride.emit, url)
        rows.append([(ride, open_ride_url), end_time, car_license, "", ride_comment])


    def _should_skip_due_to_end_time(self, end_time):
        if end_time:
            try:
                end_time_dt = self._parse_time(end_time)
                return end_time_dt and end_time_dt <= dt.now() - timedelta(minutes=30)
            except Exception:
                return False
    
    @utils.retry(allow_falsy=True)
    def _retrieve_ride_details(self, ride: str):
        ride_url = self._build_ride_url(ride)
        self._open_ride_page(ride_url)

    def _build_ride_url(self, ride):
        return f'{settings.goto_url}/index.html#/orders/{ride}/details'
    
    @utils.retry(allow_falsy=True)
    def _get_ride_comment(self, page):
        try:
            return RidePage(page).ride_comment.input_value().strip()
        except Exception:
            return None
    
    @utils.retry()
    def _get_car_license(self, page):
        try:
            return RidePage(page).car_license.text_content()
        except Exception as e:
            return None
    
    @utils.retry()
    def _open_ride_page(self, ride_url: str):
        # self.web_access.create_new_page("ride", str(settings.goto_url), open_mode="reuse")
        self.web_access.create_new_page("goto_bo", ride_url, open_mode="replace")
        return self.web_access.pages['goto_bo']

    def _parse_time(self, time_str: str, dt_format: str = "%d/%m/%Y %H:%M") -> dt | None:
        try:
            return dt.strptime(time_str, dt_format) if time_str else None
        except Exception as e:
            return None

    def _notify_late_ride(self, ride, end_time, future_ride_time):
        msg = f"Ride {ride} ended at {end_time}."
        msg += f"\nNext ride at {future_ride_time}" if future_ride_time else "\nNo future ride found."
        self.show_toast(
            "Goto ~ Late Alert!",
            msg,
            icon=utils.resource_path(settings.app_icon)
        )
    
    @utils.retry(allow_falsy=False)
    def fetch_end_time(self, page):
        page.wait_for_timeout(1000)
        return RidePage(page).ride_end_time.text_content()

    @utils.retry(allow_falsy=False)
    def fetch_start_time(self, page):
        page.wait_for_timeout(1000)
        return RidePage(page).ride_start_time.text_content()
    

        
    
