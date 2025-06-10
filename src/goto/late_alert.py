from functools import partial
import os
from time import sleep
import settings
from services import WebAccess, TinyDatabase, QueryBuilder
from datetime import datetime as dt, timedelta
from src.pages import RidesPage, RidePage
class LateAlert:
    def __init__(self, db:TinyDatabase, show_toast, gui_table_row, web_access: WebAccess, open_ride):
        self.db = db
        self.show_toast = show_toast
        self.gui_table_row = gui_table_row
        self.web_access = web_access
        self.open_ride = open_ride
        
    def start_requests(self):
        self.web_access.create_new_page("goto_bo", "https://car2gobo.gototech.co/index.html#/orders/current/", "reuse")
        late_rides = self.fetch_late_ride()
        
        if not late_rides:
            self.gui_table_row([["No late reservations found", "0", "0", "0"]], btn_colors=("1d5cd0", "392890","1f1f68"))
            return self._notify_no_late_reservations()
        
        self.rows = []
        for ride in late_rides:
            self._process_ride(ride)
        self.gui_table_row(self.rows, btn_colors=("1d5cd0", "392890","1f1f68"))
        self.resolve_rides(late_rides)
        
        for row in self.rows:
            ride_id, end_time, _, future_ride_time = row
            self._notify_late_ride(ride_id, end_time, future_ride_time)

    def _notify_no_late_reservations(self):
        self.show_toast(
            "Goto ~ Late Alert!",
            "No late reservations found",
            icon=os.path.abspath(settings.app_icon)
        )

    def _process_ride(self, ride: tuple[str,str]):
        if data := self.db.find_one({'ride_id': ride}, 'goto'):
            if self._should_skip_due_to_end_time(data):
                return
            end_time, future_ride_time = data.get('end_time', None), data.get('future_ride_time', None)
        else:
            end_time, future_ride_time = self._fetch_and_store_ride_times(ride)
        
        open_future_ride = None
        if ride[1]:
            future_ride_url = self._build_ride_url(ride[1])
            open_future_ride = partial(self.open_ride, future_ride_url)
        future_ride_info = (ride[1], open_future_ride) if ride[1] else "No future ride"

        url = self._build_ride_url(ride[0])
        open_ride_url = partial(self.open_ride.emit, url)
        self.rows.append([(ride[0], open_ride_url), end_time, future_ride_info , future_ride_time])


    def _should_skip_due_to_end_time(self, data):
        end_time_str = data.get('end_time')
        if end_time_str:
            try:
                end_time_dt = dt.strptime(end_time_str, "%d/%m/%Y %H:%M")
                return end_time_dt <= dt.now() - timedelta(minutes=30)
            except Exception as e:
                pass
        return False

    def _fetch_and_store_ride_times(self, ride: tuple[str, str]):
        ride_url = self._build_ride_url(ride[0])
        self._open_ride_page(ride_url)
        end_time = self._get_end_time(self.web_access.pages['goto_bo'])
        future_ride_time = None
        if ride[1]:
            future_ride_url = self._build_ride_url(ride[1])
            self.web_access.create_new_page("goto_bo", future_ride_url, open_mode="replace")
            
            future_ride_time = self._get_future_ride_time(self.web_access.pages['goto_bo'])
            
        self._store_ride_times(ride[0], end_time, future_ride_time)
        return end_time, future_ride_time

    def _build_ride_url(self, ride):
        return f'{settings.goto_url}/index.html#/orders/{ride}/details'

    def _open_ride_page(self, ride_url: str):
        # self.web_access.create_new_page("ride", str(settings.goto_url), open_mode="reuse")
        self.web_access.create_new_page("goto_bo", ride_url, open_mode="replace")
        return self.web_access.pages['goto_bo']

    def _get_end_time(self, page):
        end_time = self.fetch_end_time(page)
        return self._parse_time(end_time, "end_time")
    
    def _get_start_time(self, page):
        start_time = self.fetch_start_time(page)
        return self._parse_time(start_time, "start_time")

    
    def _get_future_ride_time(self, page):
        future_ride_time = self.fetch_future_ride(page)
        return self._parse_time(future_ride_time, "future ride time")

    def _store_ride_times(self, ride, end_time, future_ride_time):
        db_ride = {
            'ride_id': ride,
            'end_time': end_time,
            'future_ride_time': future_ride_time,
            'resolved_time': None
        }
        self.db.upsert_one(db_ride, 'goto')

    def _parse_time(self, time_str, label):
        try:
            return dt.strptime(time_str, "%d/%m/%Y %H:%M").strftime("%d/%m/%Y %H:%M") if time_str else None
        except Exception as e:
            pass
        return None

    def _notify_late_ride(self, ride, end_time, future_ride_time):
        msg = f"Ride {ride} ended at {end_time}."
        msg += f"\nNext ride at {future_ride_time}" if future_ride_time else "\nNo future ride found."
        self.show_toast(
            "Goto ~ Late Alert!",
            msg,
            icon=os.path.abspath(settings.app_icon)
        )
    
    def resolve_rides(self, rides):
        """
        This function resolves the rides in the database.
        :param rides: List of ride IDs to resolve
        """
        query = QueryBuilder.query({ 'resolved_time': None })
        data = self.db.search_by(query, 'goto')
        rides_ids = [ride[0] for ride in rides]
        for data_item in data:
            ride_id = data_item.get('ride_id')
            if ride_id not in rides_ids:
                resolved_time = dt.now().strftime("%d/%m/%Y %H:%M")
                data_item['resolved_time'] = resolved_time
                self.db.upsert_one(data_item, 'goto')

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
        
    
    def fetch_future_ride(self, page):
        try:
            return self._get_start_time(page)
        except Exception as e:
            return ""
