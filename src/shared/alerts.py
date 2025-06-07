    # page.locator("html").click()
    # page.get_by_role("menuitem", name="Notifications").click()
    # page.get_by_text("4 minutes ago", exact=True).click()
    # page.get_by_label("New Mention notification: חשד לגניבת רכב רכב נמצא מעבר לקו הירוק - אנא בדיקתכם. [click here to open](https://goto.crm4.dynamics.com/main.aspx?appid=0f6cc0bf-abf5-e811-a953-000d3a464508&pagetype=entityrecord&etn=email&id=c9f7d4a8-ba43-f011-877a-6045bdf62736)", exact=True).get_by_text("חשד לגניבת רכב").click()
    # page.get_by_label("New Mention notification: חשד לגניבת רכב רכב נמצא מעבר לקו הירוק - אנא בדיקתכם. [click here to open](https://goto.crm4.dynamics.com/main.aspx?appid=0f6cc0bf-abf5-e811-a953-000d3a464508&pagetype=entityrecord&etn=email&id=c9f7d4a8-ba43-f011-877a-6045bdf62736)", exact=True).get_by_role("link", name="click here to open").click(modifiers=["ControlOrMeta"])
    # page1 = context.new_page()
    # page1.goto("https://goto.crm4.dynamics.com/main.aspx?appid=0f6cc0bf-abf5-e811-a953-000d3a464508&pagetype=entityrecord&etn=email&id=c9f7d4a8-ba43-f011-877a-6045bdf62736")
    # page1.goto("https://goto.crm4.dynamics.com/main.aspx?appid=0f6cc0bf-abf5-e811-a953-000d3a464508&pagetype=entityrecord&etn=email&id=c9f7d4a8-ba43-f011-877a-6045bdf62736")
    # page.get_by_label("New Mention notification: חשד לגניבת רכב רכב נמצא מעבר לקו הירוק - אנא בדיקתכם. [click here to open](https://goto.crm4.dynamics.com/main.aspx?appid=0f6cc0bf-abf5-e811-a953-000d3a464508&pagetype=entityrecord&etn=email&id=c9f7d4a8-ba43-f011-877a-6045bdf62736)", exact=True).get_by_role("button", name="Dismiss notification").click()
    # page.get_by_role("button", name="Dismiss all").click()
    # page1.goto("https://goto.crm4.dynamics.com/main.aspx?appid=0f6cc0bf-abf5-e811-a953-000d3a464508&pagetype=entityrecord&etn=email&id=c9f7d4a8-ba43-f011-877a-6045bdf62736")
    # page1.get_by_role("textbox", name="Subject").click()
    # page1.locator("iframe[title=\"Description\"]").content_frame.get_by_text("carNickName:").click(button="right")
    # page1.locator("iframe[title=\"Description\"]").content_frame.get_by_text("carNickName:").click()
    # page1.locator("iframe[title=\"Description\"]").content_frame.get_by_text("carNickName: , carId: 3002048").click(button="right")
    # page1.locator("iframe[title=\"Description\"]").content_frame.get_by_text("carNickName:").click(button="right")

    # ----------------
    # # ---------------------
    
from services import WebAccess
from src import pages


class Alerts:
    """
    A class to represent the location of a pointer in a 2D space.
    """

    def __init__(self, webaccess: WebAccess, pointer, table):
        """
        Initializes the PointerLocation with a WebAccess instance.

        :param webaccess: An instance of WebAccess to interact with the web page.
        """
        self.webaccess = webaccess
        self.pointer = pointer
        self.table = table
    
    def start_requests(self):
        """
        Starts the requests to fetch alerts.
        """
        goto_crm_page = self.webaccess.pages['goto_crm']
        autotel_crm_page = self.webaccess.pages['autotel_crm']
        
        if not goto_crm_page.is_visible('//h1[text()="Notifications"]'):
            goto_crm_page.get_by_role("menuitem", name="Notifications").click()
            
        if not autotel_crm_page.is_visible('//h1[text()="Notifications"]'):
            autotel_crm_page.get_by_role("menuitem", name="Notifications").click()