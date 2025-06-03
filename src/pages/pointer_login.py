class PointerLoginPage:
    def __init__(self, page):
        self.page = page

    def login(self, username, phone):
        self.driver.find_element("id", "username").send_keys(username)
        self.driver.find_element("id", "password").send_keys(password)
        self.driver.find_element("id", "login-button").click()

    def is_login_successful(self):
        return "Welcome" in self.driver.page_source
    
    # row0 td:nth-child(13)
    #     page.get_by_role("textbox", name="שם משתמש").click()
    # page.get_by_role("textbox", name="שם משתמש").press("ControlOrMeta+r")
    # page.get_by_role("textbox", name="שם משתמש").press("ControlOrMeta+r")
    # page.get_by_role("textbox", name="מספר נייד").click()
    # page.get_by_role("textbox", name="מספר נייד").fill("0547311577")
    # page.locator("#button_otp").click()
    # page.get_by_text("-").fill("-5")