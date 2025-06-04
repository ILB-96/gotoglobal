from time import sleep
from playwright.sync_api import Page

class RidePage:
    def __init__(self, page: Page):
        self.page = page
    
    def fetch_end_time(self):
        sleep(5)
        return self.page.locator('(//td[contains(@title, "End Time")])[1]//following-sibling::td').text_content()