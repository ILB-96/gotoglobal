from services import AsyncWebAccess
from src import pages


class PointerLocation:
    """
    A class to represent the location of a pointer in a 2D space.
    """

    def __init__(self, webaccess: AsyncWebAccess):
        """
        Initializes the PointerLocation with a WebAccess instance.

        :param webaccess: An instance of WebAccess to interact with the web page.
        """
        self.webaccess = webaccess
    
    
    async def login(self, user, phone):
        """
        Logs in to the Pointer service using the provided account credentials.
        """
        login_page = pages.PointerLoginPage(self.webaccess.pages['pointer'])
        await login_page.login(user, phone)

    async def fill_otp(self, otp: str):
        """
        Fills the OTP input field with the provided OTP.

        :param otp: The one-time password to fill in the input field.
        """
        login_page = pages.PointerLoginPage(self.webaccess.pages['pointer'])
        await login_page.fill_otp(otp)
    
    async def search_location(self, query: str):
        """
        Searches for a location using the provided query string.

        :param query: The location query to search for.
        """
        pointer_page =  pages.PointerPage(self.webaccess.pages['pointer'])
        data = await pointer_page.get_first_row_data(query)
        return data
