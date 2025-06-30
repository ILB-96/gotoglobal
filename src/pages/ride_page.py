from playwright.async_api import Page

class RidePage:
    def __init__(self, page: Page):
        self.page = page
    
    @property
    def ride_end_time(self):
        """
        Fetches the end time of the ride.
        :return: End time as a Locator for the text input
        """
        return self.page.locator('[title="End Time"] + td')
    
    @property
    def ride_start_time(self):
        """
        Fetches the start time of the ride.
        :return: Start time as a Locator for the text input
        """
        return self.page.locator('[title="Start Time"] + td')
    
    @property
    def car_license(self):
        """
        Fetches the car ID associated with the ride.
        :return: Car ID as a locator for the text input
        """
        return self.page.locator('[ng-click="orderDetailsCtrl.showCarDetails()"]')
    
    @property
    def ride_comment(self):
        """
        Fetches the comment associated with the ride.
        :return: Comment as a locator for the textarea
        """
        return self.page.locator('textarea[ng-blur="orderDetailsCtrl.updateReservationFields()"]')
    