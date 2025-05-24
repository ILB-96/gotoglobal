
from functools import partial
import os
from time import sleep
import settings
from services import WebAccess
import pyperclip

from win11toast import toast

class LateAlert:
    def __init__(self, db):
        self.db = db
        # self.toaster = WindowsBalloonTip()

    def start_requests(self, playwright):
        with WebAccess(playwright, settings.playwright_headless, str(settings.profile)) as web_access:
            
            web_access.start_context(str(settings.goto_url), "")

            late = self.get_late_reservations(web_access)
            if late:
                for reservation in late:
                    reservation_url = f'{settings.goto_url}/index.html#/orders/{reservation}/details'
                    web_access.new_tab(reservation_url)
                    toast(
                        "Goto ~ Late Alert!",
                        reservation,
                        buttons=[{'activationType': 'protocol', 'arguments': str(reservation), 'content': 'Copy Reservation #'}, "Dismiss"],
                        icon=os.path.abspath("c2gFav.ico"),
                    )
            else:
                toast("Goto ~ Late Alert!", "No late reservations found")

    def get_late_reservations(self, web_access: WebAccess):
        """
        This function checks for late reservations.
        :param web_access: WebAccess instance
        :return: List of late reservations
        """
        late_reserv_frame = web_access.page.get_by_text("</form> </div> </div>").content_frame.get_by_text("A2A - Late Reservations Reservation that customer is far from parking")
        return {locator.text_content() for locator in late_reserv_frame.locator('#billingReceipetSpan h3').all()}
    
    def on_click(self, message):
        """
        This function is called when the toast notification is clicked.
        :param message: The message to be copied to clipboard
        """
        pyperclip.copy(message)
    
