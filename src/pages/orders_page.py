import re
from playwright.sync_api import Page

class OrdersPage:
    def __init__(self, page: Page):
        self.page = page
        
    def late_rides_frame(self):
        return self.page.get_by_text("</form> </div> </div>").content_frame.get_by_text("A2A - Late Reservations Reservation that customer is far from parking")
    
    def get_late_rides(self):
        """
        Fetches late rides from the late rides frame.
        :return: List of late rides
        """        
        entries = self.late_rides_frame().locator('#billingReceipetSpan h3').all()
        grouped_data = []

        for h3 in entries:
            h3_text = str(h3.text_content()).strip()
            
            sibling_p = h3.evaluate_handle("node => node.nextElementSibling && node.nextElementSibling.tagName === 'P' ? node.nextElementSibling : null")
            
            if sibling_p:
                p_text = sibling_p.evaluate("node => node.textContent").strip()
                match = re.search(r'Next (\d+)', p_text)
                if match:
                    p_text = match.group(1)
                else:
                    p_text = None
            else:
                p_text = None

            grouped_data.append((h3_text, p_text))
        return grouped_data
    
    def bo_search(self, search_value):
        """
        This function performs a search on the page.
        :param page: The page to perform the search on
        :param search_value: The value to search for
        """
        self.page.get_by_role("textbox", name="Search").click()
        self.page.get_by_role("textbox", name="Search").fill(search_value)
        self.page.get_by_role("button", name="Search").click()