from services import WebAccess
from src import pages


class PointerLocation:
    """
    A class to represent the location of a pointer in a 2D space.
    """

    def __init__(self, webaccess: WebAccess):
        """
        Initializes the PointerLocation with a WebAccess instance.

        :param webaccess: An instance of WebAccess to interact with the web page.
        """
        self.webaccess = webaccess
    
    
    def login(self, account: dict):
        """
        Logs in to the Pointer service using the provided account credentials.
        """
        pages.PointerLoginPage(self.webaccess.pages['pointer']).login(
            username=account.get('pointer_user', account.get('username', '')),
            phone=account.get('phone', '')
        )

    def fill_otp(self, otp: str):
        """
        Fills the OTP input field with the provided OTP.

        :param otp: The one-time password to fill in the input field.
        """
        pages.PointerLoginPage(self.webaccess.pages['pointer']).fill_otp(otp)
    
    def search_location(self, query: str):
        """
        Searches for a location using the provided query string.

        :param query: The location query to search for.
        """
        return pages.PointerPage(self.webaccess.pages['pointer']).get_first_row_data(query)
        
        
        