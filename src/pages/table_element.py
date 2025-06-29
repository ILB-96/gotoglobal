
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
    
    def row_6th_cell(self, row):
        """
        Returns the 6th cell of a given row.
        :param row: The row locator.
        :return: Locator for the 6th cell in the row.
        """
        return row.locator('td:nth-child(6)')

    def row_3rd_cell(self, row):
        """
        Returns the 3rd cell of a given row.
        :param row: The row locator.
        :return: Locator for the 3rd cell in the row.
        """
        return row.locator('td:nth-child(3)')