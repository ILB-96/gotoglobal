from playwright.sync_api import Page

class PointerLoginPage:
    def __init__(self, page: Page):
        self.page = page
    
    @property
    def username_input(self):
        return self.page.get_by_role("textbox", name="שם משתמש")
    
    @property
    def phone_input(self):
        return self.page.get_by_role("textbox", name="מספר נייד")
    
    @property
    def login_button(self):
        return self.page.locator("#button_otp")
    
    def login(self, username, phone):
        self.username_input.click()
        self.username_input.fill(username)
        self.phone_input.click()
        self.phone_input.fill(phone)
        self.page.locator("#button_otp").click()

    def fill_otp(self, otp):
        self.page.wait_for_selector('textarea.realInput', timeout=10000)
        self.page.focus('textarea.realInput')
        for digit in otp:
            if digit.isdigit():
                self.page.keyboard.press(digit)
                self.page.wait_for_timeout(500)
            else:
                continue