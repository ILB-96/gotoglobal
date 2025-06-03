class PointerPage:
    def __init__(self, page):
        self.page = page
    
    def search(self, search_text):
        search_box = self.page.get_by_role("textbox", name="חיפוש")
        search_box.click()
        search_box.fill(search_text)
    
    def get_first_row_data(self):
        first_row = self.page.locator("row0 td:nth-child(13)")
        return first_row.text_content() if first_row else None

    