
import settings
from services import WebAccess
from services import Log
from time import sleep
import pyperclip
from utils import WindowsBalloonTip

class LateAlert:
    def __init__(self, db):
        self.db = db
        self.toaster = WindowsBalloonTip()
        self.toaster.ShowWindow("Goto ~ Late Alert!", "Late Alert Initialized")

    def start_requests(self, playwright):
        with WebAccess(playwright, settings.playwright_headless, settings.profile) as web_access:
            
            web_access.start_context(settings.goto_url, "")

            late = self.get_late_reservations(web_access)
            if late:
                
                for reservation in late:
                    Log.info(f"Late Alert: {reservation}")
                    self.toaster.ShowWindow("Goto ~ Late Alert!", reservation)

            else:
                self.toaster.ShowWindow("Goto ~ Late Alert!", "No late reservations found")


    def get_late_reservations(self, web_access: WebAccess):
        """
        This function checks for late reservations.
        :param web_access: WebAccess instance
        :return: List of late reservations
        """
        late_reserv_frame = web_access.page.get_by_text("</form> </div> </div>").content_frame.get_by_text("A2A - Late Reservations Reservation that customer is far from parking")
        return {locator.text_content() for locator in late_reserv_frame.locator('#billingReceipetSpan h3').all()}
    

    def show_toast(self, message, icon_path, timeout=8000):
        def command():
            pyperclip.copy(message)

        self.toaster.show_toast(
            title="Goto ~ Late Alert!",
            msg=message,
            icon_path=icon_path,
            duration=timeout,
            threaded=False,
            callback_on_click=command
        )
        
            
