from playwright.async_api import Page

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
    
    async def login(self, username, phone):
        await self.username_input.click()
        await self.username_input.fill(username)
        await self.phone_input.click()
        await self.phone_input.fill(phone)
        await self.page.locator("#button_otp").click()

    async def fill_otp(self, otp):
        await self.page.wait_for_selector('textarea.realInput', timeout=10000)
        await self.page.focus('textarea.realInput')
        for digit in otp:
            if digit.isdigit():
                await self.page.keyboard.press(digit)
                await self.page.wait_for_timeout(200)
            else:
                continue