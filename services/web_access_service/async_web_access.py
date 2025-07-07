from pathlib import Path
import subprocess
from time import sleep
from playwright.async_api import BrowserContext, Page, Playwright, Download
from typing import Optional
from pathlib import Path

class AsyncWebAccess:
    """
    Asynchronous Playwright wrapper.
    Usage:
        async with async_playwright() as p:
            async with AsyncWebAccess(p, headless=False, profile="Default") as web:
                await web.create_pages({...})
    """

    def __init__(
        self,
        playwright: Playwright,
        headless: bool = True,
        browser_name: str = 'edge',
        profile: str = "Default",
    ):
        self._playwright = playwright
        self._headless = headless
        self._browser_name = browser_name
        self._profile = profile or None
        self.pages: dict[str, Page] = {}
        
    async def __aenter__(self):
        if self._profile == "Port":
            try:
                self.browser = await self._playwright.chromium.connect_over_cdp('http://localhost:9222', timeout=10000)
                self.context = self.browser.contexts[0] if self.browser.contexts else await self.browser.new_context()
            except Exception:
                subprocess.call(['taskkill', '/F', '/IM', 'msedge.exe'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.call([
                    'start', 'msedge', '--remote-debugging-port=9222', '--no-first-run'
                ], shell=True)
                sleep(5)
                self.browser = await self._playwright.chromium.connect_over_cdp('http://localhost:9222')
                self.context = self.browser.contexts[0] if self.browser.contexts else await self.browser.new_context()

        elif self._profile:
            if self._browser_name == 'chrome':
                BROWSER_PATH = Path("C:/Program Files/Google/Chrome/Application/chrome.exe")
                user_data_dir = (
                    Path.home()
                    / "AppData"
                    / "Local"
                    / "Google"
                    / "Chrome"
                    / "User Data"
                    / self._profile
                )
            else:    
                BROWSER_PATH = Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")
                user_data_dir = (
                    Path.home()
                    / "AppData"
                    / "Local"
                    / "Microsoft"
                    / "Edge"
                    / self._profile
                )
                self.context = await self._playwright.chromium.launch_persistent_context(
                    user_data_dir=user_data_dir.parent,
                    headless=self._headless,
                    executable_path=BROWSER_PATH,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-infobars'],
                )
                self.browser = self.context.browser
        else:
            self.browser = await self._playwright.chromium.launch(
                headless=self._headless)
            self.context: BrowserContext = await self.browser.new_context()
        
        await self.add_download_event_handler()
            
        self.pages: dict[str, Page] = {}
        await self.block_unwanted_requests(self.context)
                
        return self
    async def block_unwanted_requests(self, context):
        urls_to_block = {"https://car2govisibility.gototech.co/API/RT/reservationIssues",
                         'content.powerapps.com/resource/webplayerbus/hashedresources/2jc6enofp9rqe/js/webplayer-authflow.js',
                         'content.powerapps.com/resource/webplayerbus/hashedresources/2jc6enofp9rqe/js/webplayer-authflow.js',
                         "chrome-extension://hokifickgkhplphjiodbggjmoafhignh/fonts/fabric-icons.woff",
                         'autotel.crm4.dynamics.com/%7b000000520173284%7d/webresources/cc_MscrmControls.Grid.PCFGridControl/PCFGridControl.js',
                         "goto.crm4.dynamics.com/%7b638872608630000206%7d/webresources/cc_MscrmControls.FieldControls.TimerControl/css/TimerIcon.css",
                         }
        async def handle_route(route, request):
            if request.url in urls_to_block or 'goto.crm4.dynamics.com/apc/100k.gif' in request.url or 'goto.crm4.dynamics.com/api/data/v9.0/activitypointers/Microsoft.Dynamics.CRM.RetrieveTimelineWallRecords' in request.url or 'apps.powerapps.com/apphost/e/' in request.url:
                print(f"[INFO] Blocking request to {request.url}")
                await route.abort()
            else:
                await route.continue_()
        
        await context.route("**/*", handle_route)
    async def add_download_event_handler(self):
        """
        Attach download event handlers only once per page,
        including future pages created in this browser context.
        """
        if not self.context:
            return

        async def handle_download(download: Download):
            await download.save_as(Path.home() / "Downloads" / download.suggested_filename)

        def attach_listener(page):
            page.on("download", handle_download)

        for page in self.context.pages:
            attach_listener(page)

        self.context.on("page", attach_listener)


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.context:
                await self.context.close()
        except Exception as e:
            print(f"[WARN] Failed to close context: {e}")

        try:
            if self.browser:
                await self.browser.close()
        except Exception as e:
            print(f"[WARN] Failed to close browser: {e}")

        # Do not suppress exceptions from the `with` block
        return False


    async def start_context(self, ignore_patterns: str = "**/*.{png,jpg,jpeg,css,svg}"):
        if not self.context:
            raise RuntimeError("Context not initialized")
        await self.context.route(ignore_patterns, lambda route: route.abort())  

    async def create_pages(self, pages: dict[str, str]):
        if not self.context:
            raise RuntimeError("Context not initialized")
        
        for name, url in pages.items():
            try:
                await self.create_new_page(name, url, wait_until="domcontentloaded")
            except Exception:
                self.pages[name] = await self.context.new_page()

        # self.pages['blank'] = await self.create_new_page('blank', 'about:blank', open_mode='reuse')

    from typing import Literal

    async def create_new_page(
        self,
        page_name: str,
        url: str,
        open_mode: str = "close",
        timeout: int = 45_000,
        wait_until: Literal['commit', 'domcontentloaded', 'load', 'networkidle'] = "networkidle",
    ) -> Page:
        if open_mode == "close" and page_name in self.pages and not self.pages[page_name].is_closed():
            old = self.pages[page_name]
            if not old.is_closed():
                await old.close()

        if page_name not in self.pages or self.pages[page_name].is_closed():
            page = await self.context.new_page()
            self.pages[page_name] = page
        else:
            page = self.pages[page_name]

        await page.goto(url, timeout=timeout, wait_until=wait_until)
        return page

    def get_page(self, page_name: str) -> Optional[Page]:
        """
        Get a page by its name.
        :param page_name: Name of the page to retrieve.
        :return: Page object or None if not found.
        """
        return self.pages.get(page_name)
    
    async def close_page(self, page_name: str):
        """
        Close a page by its name.
        :param page_name: Name of the page to close.
        """
        if page_name not in self.pages:
            return
        
        page = self.pages[page_name]
        if not page.is_closed():
            await page.close()
        del self.pages[page_name]


    async def cleanup(self):
        if self.context:
            await self.context.close()
