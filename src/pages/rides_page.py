from time import sleep
from typing import Literal
from playwright.sync_api import Page

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
    
    @property
    def orders_table_rows(self):
        return TableElement(self.page).table_rows
    
    def late_rides_frame(self):
        return self.page.get_by_text("</form> </div> </div>").content_frame.get_by_text("A2A - Late Reservations Reservation that customer is far from parking")
    

    def late_rides_entries(self):
        """
        Fetches late rides entries from the late rides frame.
        :return: List of late rides entries
        """
        return self.late_rides_frame().locator('#billingReceipetSpan h3').all()
    
    def set_ride_duration_sort(self, order: Literal["asc", "desc"]):
        """
        Sets the duration sort order for the orders table.
        :param order: "asc" for ascending, "desc" for descending
        """
        self.table_duration_button().click()
        sleep(0.5)
        self.table_duration_button().click()
            
    def get_ride_id_from_row(self, row):
        """
        Extracts the ride ID from a table row.
        :param row: The table row element
        :return: Ride ID as a string
        """
        return row.locator('[ng-click*="ordersCtrl.goToDetailsNewTab(row, $event)"]')
    
    def get_driver_id_from_row(self, row):
        """
        Extracts the ride ID from a table row.
        :param row: The table row element
        :return: Ride ID as a string
        """
        return row.locator('[ng-click="ordersCtrl.editDriverDetails(row, $event)"]')
    
    def get_car_id_from_row(self, row):
        """
        Extracts the ride ID from a table row.
        :param row: The table row element
        :return: Ride ID as a string
        """
        return row.locator('[ng-click="ordersCtrl.showCarDetails(row)"]')
    
    def get_duration_from_row(self, row):
        """
        Extracts the duration from a table row.
        :param row: The table row element
        :return: Duration as a string
        """
        return row.locator('[ng-if="ordersCtrl.pageType === \'current\'"]')
    
    def get_late_rides(self):
        grouped_data = []
        for h3 in self.late_rides_entries():
            h3_text = str(h3.text_content()).strip()

            p_text = h3.evaluate("""
                node => {
                    const p = node.nextElementSibling;
                    if (p && p.tagName === 'P') {
                        const match = p.textContent.match(/Next (\\d+)/);
                        return match ? match[1] : null;
                    }
                    return null;
                }
            """)
            grouped_data.append((h3_text, p_text))
        return grouped_data

