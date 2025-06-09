from time import sleep
from playwright.sync_api import Page

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
    
    @property
    def rows(self):
        return self.page.locator("#CarTableInfo tbody tr")
    
    def get_first_row_data(self, search_text):
        # Find the specific <tr> where the second <td> contains the search text
        matching_row = self.rows.filter(
            has=self.page.locator("td", has_text=search_text))
  
        if matching_row.count() == 0:
            return "No results"
        
        return matching_row.locator("td").nth(12).inner_text().strip()

