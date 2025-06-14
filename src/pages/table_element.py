
from playwright.sync_api import Page

class TableElement:
    def __init__(self, page: Page):
        self.page = page
    
    @property
    def table_rows(self):
        """
        Returns the rows of the table.
        :return: A list of rows in the table.
        """
        return self.page.locator('tr[ng-repeat*="row in $data"]').all()