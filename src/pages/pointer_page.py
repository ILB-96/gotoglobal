from time import sleep


class PointerPage:
    def __init__(self, page):
        self.page = page
    
    def search(self, search_text):
        search_box = self.page.get_by_role("textbox", placeholder="חיפוש")
        search_box.click()
        search_box.fill(search_text)
        sleep(5)
        return self.get_first_row_data(search_text)
    
    def get_first_row_data(self, search_text):
        result_rows = self.page.locator('//table[@id="CarTableInfo"]//tbody//tr').all()
        for row in result_rows:
            car_liscense = row.locator("td[2]").inner_text()
            if car_liscense == search_text:
                return row.locator("td[13]").inner_text()
        return "No results"

    