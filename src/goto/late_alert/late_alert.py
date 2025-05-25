
from functools import partial
import os
from time import sleep
import settings
from services import WebAccess, Log
import pyperclip

from win11toast import toast

class LateAlert:
    def __init__(self, db):
        self.db = db
        reservation = '123123'
        self.handler_path = os.path.abspath("handler.pyw")
        Log.info(f"LateAlert initialized with handler path: {self.handler_path}")
        msg = f"Reservation {reservation} is late."
        result = toast(
            "Goto ~ Late Alert!",
            f"Reservation {reservation} is late.\nClick to copy to clipboard.",
            on_click=f'"{self.handler_path}" {reservation}',  # full command with argument
            icon=os.path.abspath("c2gFav.ico")
        )
        result.add_done_callback(partial(self.on_toast_click, reservation))

    def on_toast_click(self, reservation, future):
        until
    def start_requests(self, playwright):
        with WebAccess(playwright, settings.playwright_headless, str(settings.profile)) as web_access:
            
            web_access.start_context(str(settings.goto_url), "")
            
            late = self.get_late_reservations(web_access)
            if late:
                for reservation in late:
                    reservation_url = f'{settings.goto_url}/index.html#/orders/{reservation}/details'
                    future = self.get_future_reservation(web_access, reservation_url)
                    msg = f"Reservation {reservation} is late."
                    msg += f"\nFuture reservation: {future}" if future else ""
                    toast(
                        "Goto ~ Late Alert!",
                        f"Reservation {reservation} is late.\nClick to copy to clipboard.",
                        on_click=f'"{self.handler_path}" {reservation}',  # full command with argument
                        icon=os.path.abspath("c2gFav.ico")
                    )
            else:
                toast("Goto ~ Late Alert!", "No late reservations found")

    def get_late_reservations(self, web_access: WebAccess):
        """
        This function checks for late reservations.
        :param web_access: WebAccess instance
        :return: List of late reservations
        """
        late_reserv_frame = web_access.pages[0].get_by_text("</form> </div> </div>").content_frame.get_by_text("A2A - Late Reservations Reservation that customer is far from parking")
        return {locator.text_content() for locator in late_reserv_frame.locator('#billingReceipetSpan h3').all()}
    
    def get_future_reservation(self, web_access: WebAccess, reservation_url):
        page_index = web_access.new_tab(str(settings.goto_url))
        page = web_access.pages[page_index]
        
        page.goto(reservation_url)
        
        page.locator('//*[contains(@ng-click, "showCarDetails")]').click()
        page.get_by_role("button", name="Future reservations").click()
        sleep(10)
        try:
            future_reservations = page.locator('div:nth-child(4) > .details-block-table .table-body tr:nth-child(1) [ng-switch-when="dateAndTimeShort"]').all()
            return future_reservations[0].text_content() if future_reservations else ""
        except Exception as e:
            Log.error(f"Error getting future reservation: {e}")
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
