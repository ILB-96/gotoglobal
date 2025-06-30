from time import sleep
from typing import Literal
from playwright.async_api import Page, Locator

from .table_element import TableElement

class RidesPage:
    def __init__(self, page: Page):
        self.page = page
        

    def table_duration_button(self):
        """
        Returns the button to sort the table by duration.
        :return: Locator for the duration button
        """
        return self.page.get_by_role("button", name="Duration")
    
    def table_duration_sort_state(self):
        """
        Returns the current sort state of the duration button.
        :return: "asc" if sorted ascending, "desc" if sorted descending, None if not sorted
        """
        return str(self.page.locator("th", has=self.table_duration_button()).get_attribute("class"))
    

    async def orders_table_rows(self):
        return await TableElement(self.page).table_rows()
    
    @property
    def car_license_input(self):
        """
        Returns the input field for car license search.
        :return: Locator for the car license input field
        """
        return self.page.locator('[ng-model="ordersCtrl.filterFields.carLicencePlate"]')

    def row_start_time_cell(self, row: Locator):
        """
        Returns the start time cell of a given row.
        :param row: The row locator.
        :return: Locator for the start time cell in the row.
        """
        return TableElement(self.page).row_6th_cell(row)
    
    async def search_by_car_license(self, car_license: str):
        """
        Searches for rides by car license.
        :param car_license: The car license to search for
        """
        await self.car_license_input.fill(car_license)

    async def late_rides_frame(self):
        """
        Finds the iframe that contains the late reservations section.
        :return: Playwright Frame object
        """
        # Find the iframe element (adjust selector if needed)
        iframe_element = self.page.locator("iframe").first
        await self.page.wait_for_timeout(500)


        await iframe_element.wait_for()

        # Get the actual frame object
        frame = await (await iframe_element.element_handle()).content_frame()

        if frame is None:
            raise Exception("Late rides iframe not found")

        # Wait for some known content to appear inside the frame
        await frame.get_by_text("A2A - Late Reservations Reservation that customer is far from parking").wait_for()

        return frame


    async def late_rides_entries(self):
        """
        Fetches late rides entries from the late rides frame.
        :return: List of h3 elements under the late rides section
        """

        try:     
            frame = await self.late_rides_frame()
            await frame.wait_for_selector('#billingReceipetSpan h3',timeout=5000)

            return await frame.locator('#billingReceipetSpan h3').all()
        except Exception:
            return []

    
    async def set_ride_duration_sort(self, order: Literal["asc", "desc"]):
        """
        Sets the duration sort order for the orders table.
        :param order: "asc" for ascending, "desc" for descending
        """
        await self.table_duration_button().click()
        if order == 'desc':
            await self.page.wait_for_timeout(1000)
            await self.table_duration_button().click()
            
    def get_ride_id_from_row(self, row: Locator):
        """
        Extracts the ride ID from a table row.
        :param row: The table row element
        :return: Ride ID as a string
        """
        return row.locator('[ng-click*="ordersCtrl.goToDetailsNewTab(row, $event)"]')
    
    def get_driver_id_from_row(self, row: Locator):
        """
        Extracts the ride ID from a table row.
        :param row: The table row element
        :return: Ride ID as a string
        """
        return row.locator('[ng-click="ordersCtrl.editDriverDetails(row, $event)"]')
    
    def get_driver_name_from_row(self, row: Locator):
        """
        Extracts the driver name from a table row.
        :param row: The table row element
        :return: Driver name as a string
        """
        return TableElement(self.page).row_3rd_cell(row)
    
    def get_car_id_from_row(self, row: Locator):
        """
        Extracts the ride ID from a table row.
        :param row: The table row element
        :return: Ride ID as a string
        """
        return row.locator('[ng-click="ordersCtrl.showCarDetails(row)"]')
    
    def get_duration_from_row(self, row: Locator):
        """
        Extracts the duration from a table row.
        :param row: The table row element
        :return: Duration as a string
        """
        return row.locator('[ng-if="ordersCtrl.pageType === \'current\'"]')
    
    async def get_late_rides(self):
        results = []
        for h3 in await self.late_rides_entries():
            text = await h3.text_content()
            if text:
                results.append(str(text).strip())
        return results
