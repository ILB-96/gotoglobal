from time import sleep
from playwright.async_api import Page

class PointerPage:
    def __init__(self, page: Page):
        self.page = page

    @property
    def rows(self):
        # Locator creation is synchronous; you do not need async here.
        return self.page.locator("#CarTableInfo tbody tr")

    async def get_first_row_data(self, search_text):
        # Locator methods (like .count(), .inner_text()) are async, but creating the locator is not.
        matching_row = self.rows.filter(
            has=self.page.locator("td", has_text=search_text))

        if await matching_row.count() == 0:
            return "No results"

        return (await matching_row.locator("td").nth(12).inner_text()).strip()
