from playwright.sync_api import Page

class RidePage:
    def __init__(self, page: Page):
        self.page = page
    
    @property
    def ride_end_time(self):
        """
        Fetches the end time of the ride.
        :return: End time as a string
        """
        return self.page.locator('(//td[contains(@title, "End Time")])[1]//following-sibling::td')
    
    @property
    def ride_start_time(self):
        """
        Fetches the start time of the ride.
        :return: Start time as a string
        """
        return self.page.locator('(//td[contains(@title, "Start Time")])[1]//following-sibling::td')
    
    