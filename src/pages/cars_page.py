from playwright.async_api import Page
from .table_element import TableElement

class CarsPage:
    def __init__(self, page: Page):
        self.page = page

    async def select_elements(self):
        return await self.page.locator("select").all()
    
    async def car_status_select(self):
        """
        Selects the car status from the dropdown.
        """
        return (await self.select_elements())[0]
    
    async def car_category_select(self):
        """
        Selects the car type from the dropdown.
        :param type: The type to select (e.g., "number:1").
        """
        return (await self.select_elements())[1]
    
    async def cars_table_rows(self):
        """
        Returns the rows of the cars table.
        :return: A list of rows in the cars table.
        """
        return await TableElement(self.page).table_rows()