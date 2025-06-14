import os
from datetime import datetime as dt
from pathlib import Path
from typing import Generator

from playwright._impl._errors import TargetClosedError
from playwright.sync_api import (
    Page,
    Playwright,
    expect,
    Locator,
    Browser,
    BrowserContext,
)

class WebAccess:
    """Provides access to web functionality."""

    def __init__(self, playwright: Playwright, headless=True, profile: str | None= None):
        """
        Initializes a WebAccess object.

        Parameters:
        - playwright (Playwright): The Playwright instance used to launch the browser.
        - headless (bool): Whether to run the browser in headless mode. Default is True.
        """
        BROWSER_PATH = Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")
        self.pages: dict[str, Page] = {}
        if profile:
            user_data_dir = Path.home() / "AppData" / "Local" / "Microsoft" / "Edge" / "User Data" / profile
            assert os.path.exists(user_data_dir)
            self.context: BrowserContext = playwright.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=headless,
                executable_path=BROWSER_PATH,
            )
        else:
            self.context: BrowserContext = playwright.chromium.launch(
                headless=headless,
                executable_path=BROWSER_PATH,
            ).new_context()


    def start_context(
        self,ignore="**/*.{png,jpg,jpeg,css,svg}"
    ):
        # Persistent context: don't recreate context

        # if not self.profile:
        #     self.context = self.browser.new_context()
        if ignore:
            self.context.route(ignore, lambda route: route.abort())
            
            
    def create_pages(self, pages: dict[str, str]):
        for page_name, url in pages.items():
            self.create_new_page(page_name, url)
        
        if self.context.pages[0].url == "about:blank":
            self.context.pages[0].close()
        

    def create_new_page(self, page_name: str, url: str, open_mode = 'close', timeout=45000, wait_until="networkidle"):
        """Opens a new tab in the browser and navigates to the specified URL.

        Args:
            url (str): The URL to navigate to.
            timeout (int, optional): The maximum time to wait for the page to load, in milliseconds. Defaults to 45000.

        Returns:
            New tab index (int): The index of the newly opened tab in the pages list.
        """
        if open_mode == 'close' and self.pages.get(page_name) and not self.pages[page_name].is_closed():
            self.pages[page_name].close()
        
        if not self.pages.get(page_name) or self.pages.get(page_name).is_closed() or open_mode == 'close':
            self.pages[page_name] = self.context.new_page()
        elif open_mode == 'reuse' and self.pages[page_name].url.startswith(url):
            return self.pages[page_name]

        self.pages[page_name].goto(url, timeout=timeout, wait_until=wait_until)
        
        return self.pages[page_name]

    

    def cleanup(self):
        """Closes the context and browser objects.

        This method is responsible for cleaning up the resources used by the web access service.
        It closes the context and browser objects to free up system resources.

        Parameters:
        - None

        Returns:
        - None
        """
        try:
            if self.context:
                self.context.close()
        except Exception as e:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
