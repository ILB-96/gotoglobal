from time import sleep
from services.logging_service.logging_service import Log


class PointerLoginPage:
    def __init__(self, page):
        self.page = page

    def login(self, username, phone):
        self.page.get_by_role("textbox", name="שם משתמש").click()
        self.page.get_by_role("textbox", name="שם משתמש").fill(username)
        self.page.get_by_role("textbox", name="מספר נייד").click()
        self.page.get_by_role("textbox", name="מספר נייד").fill(phone)
        self.page.locator("#button_otp").click()

    def fill_otp(self, otp):
        self.page.wait_for_selector('textarea.realInput', timeout=10000)
        self.page.focus('textarea.realInput')
        for digit in otp:
            if digit.isdigit():
                self.page.keyboard.press(digit)
                sleep(0.05)
            else:
                Log.error(f"Invalid OTP digit: {digit}")

    def search_location(self, query):
        search = self.page.get_by_role("textbox", placeholder="חיפוש")
        search.fill(query)
        
    # row0 td:nth-child(13)
    #     page.get_by_role("textbox", name="שם משתמש").click()
    # page.get_by_role("textbox", name="שם משתמש").press("ControlOrMeta+r")
    # page.get_by_role("textbox", name="שם משתמש").press("ControlOrMeta+r")
    # page.get_by_role("textbox", name="מספר נייד").click()
    # page.get_by_role("textbox", name="מספר נייד").fill("0547311577")
    # page.locator("#button_otp").click()
    # page.get_by_text("-").fill("-5")