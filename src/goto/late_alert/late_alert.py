import os
import re
from time import sleep
import settings
from services import WebAccess, Log, TinyDatabase, QueryBuilder
import pyperclip
from datetime import datetime as dt, timedelta
from win11toast import toast

class LateAlert:
    def __init__(self, db:TinyDatabase):
        self.db = db
        
    def start_requests(self, playwright):
        with WebAccess(playwright, settings.playwright_headless, str(settings.profile)) as web_access:
            web_access.start_context(str(settings.goto_url), "")
            late_rides = self.fetch_late_ride(web_access)
            if not late_rides:
                return self._notify_no_late_reservations()
                
            for ride in late_rides:
                self._process_ride(ride, web_access)
                
            self.resolve_rides(late_rides)

    def _notify_no_late_reservations(self):
        toast(
            "Goto ~ Late Alert!",
            "No late reservations found",
            button="Dismiss",
            icon=os.path.abspath("c2gFav.ico")
        )

    def _process_ride(self, ride: tuple[str,str], web_access: WebAccess):
        data = self.db.find_one({'ride_id': ride}, 'goto')
        # if data:
        #     if self._should_skip_due_to_end_time(data):
        #         return
        #     end_time, future_ride_time = data.get('end_time', None), data.get('future_ride_time', None)
        # else:
        end_time, future_ride_time = self._fetch_and_store_ride_times(ride, web_access)
        self._notify_late_ride(ride[0], end_time, future_ride_time)

    def _should_skip_due_to_end_time(self, data):
        end_time_str = data.get('end_time')
        if end_time_str:
            try:
                end_time_dt = dt.strptime(end_time_str, "%d/%m/%Y %H:%M")
                return end_time_dt <= dt.now() - timedelta(minutes=30)
            except Exception as e:
                Log.error(f"Error parsing end_time: {e}")
        return False

    def _fetch_and_store_ride_times(self, ride: tuple[str, str], web_access: WebAccess):
        ride_url = self._build_ride_url(ride[0])
        page = self._open_ride_page(web_access, ride_url)
        end_time = self._get_end_time(page)
        future_ride_url = self._build_ride_url(ride[1])
        page.goto(future_ride_url)
        future_ride_time = self._get_future_ride_time(page)
        self._store_ride_times(ride[0], end_time, future_ride_time)
        page.close()
        return end_time, future_ride_time

    def _build_ride_url(self, ride):
        return f'{settings.goto_url}/index.html#/orders/{ride}/details'

    def _open_ride_page(self, web_access: WebAccess, ride_url: str):
        page_index = web_access.new_tab(str(settings.goto_url))
        page = web_access.pages[page_index]
        page.goto(ride_url)
        return page

    def _get_end_time(self, page):
        end_time = self.fetch_end_time(page)
        return self._parse_time(end_time, "end_time")

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
            Log.error(f"Error parsing {label}: {e}")
        return None

    def _notify_late_ride(self, ride, end_time, future_ride_time):
        msg = f"Ride {ride} ended at {end_time}.\nClick to copy ride ID."
        msg += f"\nNext ride at {future_ride_time}" if future_ride_time else "No future ride found."
        toast(
            "Goto ~ Late Alert!",
            msg,
            on_click=lambda args: pyperclip.copy(str(ride)),
            button="Dismiss",
            icon=os.path.abspath("c2gFav.ico")
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
                Log.info(f"Resolved ride {ride_id} at {resolved_time}")

    def fetch_end_time(self, page):
        sleep(5)
        return page.locator('(//td[contains(@title, "End Time")])[1]//following-sibling::td').text_content()

    def fetch_late_ride(self, web_access: WebAccess):
        """
        This function checks for late reservations.
        :param web_access: WebAccess instance
        :return: List of late reservations
        """
        late_reserv_frame = web_access.pages[0].get_by_text("</form> </div> </div>").content_frame.get_by_text("A2A - Late Reservations Reservation that customer is far from parking")
        entries = late_reserv_frame.locator('#billingReceipetSpan h3').all()
        grouped_data = []

        for h3 in entries:
            h3_text = str(h3.text_content()).strip()

            # Try to get the next sibling paragraph
            sibling_p = h3.evaluate_handle("node => node.nextElementSibling && node.nextElementSibling.tagName === 'P' ? node.nextElementSibling : null")
            
            if sibling_p:
                p_text = sibling_p.evaluate("node => node.textContent").strip()
                match = re.search(r'Next (\d+)', p_text)
                if match:
                    p_text = match.group(1)
                else:
                    p_text = None
                
            else:
                p_text = None

            grouped_data.append((h3_text, p_text))
        return grouped_data
    
    def fetch_future_ride(self, page):
        try:
            return self._get_end_time(page)
        except Exception as e:
            Log.error(f"Error getting future ride: {e}")
            return ""
    
    def bo_search(self, page, search_value):
        """
        This function performs a search on the page.
        :param page: The page to perform the search on
        :param search_value: The value to search for
        """
        page.get_by_role("textbox", name="Search").click()
        page.get_by_role("textbox", name="Search").fill(search_value)
        page.get_by_role("button", name="Search").click()
