from time import sleep
from playwright.sync_api import Page

from services.logging_service.logging_service import Log
class PointerPage:
    def __init__(self, page: Page):
        self.page = page
    
    def search(self, search_text):
        search_box = self.page.locator("#TextBoxDriverName2")
        search_box.click()
        search_box.fill("")
        search_box.type(search_text, delay=50)
        sleep(5)
        result = self.get_first_row_data(search_text)
        return result
    
    def get_first_row_data(self, search_text):
        # Find the specific <tr> where the second <td> contains the search text
        matching_rows = self.page.locator("#CarTableInfo tbody tr")
        for i in range(matching_rows.count()):
            row = matching_rows.nth(i)
            second_cell = row.locator("td").nth(1)  # 0-based index, so nth(1) = 2nd cell
            if second_cell.inner_text().strip() == search_text:
                return row.locator("td").nth(12).inner_text().strip()
        return "No results"
