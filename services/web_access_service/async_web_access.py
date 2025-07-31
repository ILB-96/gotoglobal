import asyncio
from pathlib import Path
import subprocess
from playwright.async_api import async_playwright, BrowserContext, Page, Playwright, Download, Error
from typing import Optional, Literal
from pathlib import Path
import urllib.parse

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
        headless: bool = True,
        browser_name: str = 'edge',
        profile: str = "Default",
    ):
        self._headless = headless
        self._browser_name = browser_name
        self._profile = profile or None
        self.pages: dict[str, Page] = {}
        
    async def __aenter__(self):
        self._playwright = await async_playwright().start()
        return await self.create_connection()

    async def relaunch_browser(self):
        """
        Relaunch the browser, useful if the browser has been closed or crashed.
        """
        await self.cleanup()
        self.browser = None
        self.context = None
        self._playwright = await async_playwright().start()
        return await self.create_connection()
        
    
    async def create_connection(self):
        if self._profile == "Port":
            try:
                self.browser = await self._playwright.chromium.connect_over_cdp('http://127.0.0.1:9222', timeout=10000)
                self.context = self.browser.contexts[0] if self.browser.contexts else await self.browser.new_context()
            except Exception:
                subprocess.call(['taskkill', '/F', '/IM', 'msedge.exe'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.call([
                    'start', 'msedge', '--remote-debugging-port=9222', '--no-first-run'
                ], shell=True)
                await asyncio.sleep(5)
                self.browser = await self._playwright.chromium.connect_over_cdp('http://127.0.0.1:9222')
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
            self.context: BrowserContext | None = await self.browser.new_context()

        await self.add_download_event_handler()
            
        self.pages: dict[str, Page] = {}
        await self.block_unwanted_requests(self.context)
                
        return self
    
    async def block_unwanted_requests(self, context):
        exact_urls_to_block = {
            "https://car2govisibility.gototech.co/API/RT/reservationIssues",
            "https://d15k2d11r6t6rl.cloudfront.net/public/users/Integrators/BeeProAgency/588880_570515/editor_images/7e2578ba-94b9-42ff-91e7-445b43f53d32.png",
            "content.powerapps.com/resource/webplayerbus/hashedresources/2jc6enofp9rqe/js/webplayer-authflow.js",
            "chrome-extension://hokifickgkhplphjiodbggjmoafhignh/fonts/fabric-icons.woff",
            "autotel.crm4.dynamics.com/{000000520173284}/webresources/cc_MscrmControls.Grid.PCFGridControl/PCFGridControl.js",
            "goto.crm4.dynamics.com/{638872608630000206}/webresources/cc_MscrmControls.FieldControls.TimerControl/css/TimerIcon.css",
        }

        substrings_to_block = [
            "goto.crm4.dynamics.com/apc/100k.gif",
            "autotel.crm4.dynamics.com/apc/100k.gif",
            "apps.powerapps.com/apphost/e/"
        ]

        async def handle_route(route, request):
            url = urllib.parse.unquote(request.url)
            if url in exact_urls_to_block or any(substr in url for substr in substrings_to_block):
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

        # async def handle_download(download: Download):
        #     path = await download.path()
        #     if path:
        #         await asyncio.sleep(2)
        #         destination = Path.home() / "Downloads" / download.suggested_filename
        #         await download.save_as(destination)
        download_path = str(Path.home() / "Downloads")

        async def attach_listener(page: Page):
                try:
                    client = await page.context.new_cdp_session(page)
                    await client.send(
                        "Page.setDownloadBehavior",
                        {
                            "behavior": "allow",
                            "downloadPath": download_path
                        }
                    )
                except Exception as e:
                    print(f"[DownloadHandler] Failed to attach to page: {e}")

        tasks = [asyncio.create_task(attach_listener(page)) for page in self.context.pages]
        await asyncio.gather(*tasks)

        self.context.on("page", lambda page: asyncio.create_task(attach_listener(page)))


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()

        # Do not suppress exceptions from the `with` block
        return False


    async def start_context(self, ignore_patterns: str = "**/*.{png,jpg,jpeg,css,svg}"):
        if not self.context:
            raise RuntimeError("Context not initialized")
        await self.context.route(ignore_patterns, lambda route: route.abort())  

    async def create_pages(self, pages: dict[str, str]):
        if not self.context:
            raise RuntimeError("Context not initialized")
        tasks  = [asyncio.create_task(self.initialize_web_page(name, url)) for name, url in pages.items()]
        await asyncio.gather(*tasks)

    async def initialize_web_page(self, name, url):
        try:
            await self.create_new_page(name, url, wait_until="domcontentloaded")
        except Exception:
            try:
                self.pages[name] = await self.context.new_page()
            except Exception as e:
                print(f"[ERROR] Failed to create page '{name}': {e}")

        # self.pages['blank'] = await self.create_new_page('blank', 'about:blank', open_mode='reuse')

    async def create_new_page(
        self,
        page_name: str,
        url: str,
        open_mode: str = "close",
        timeout: int = 45_000,
        wait_until: Literal['commit', 'domcontentloaded', 'load', 'networkidle'] = "networkidle",
    ) -> Page:
        try:
            return await self.create_or_navigate_page(page_name, url, open_mode, timeout, wait_until)
        except Error as e:
            print(f"[ERROR] Failed to create or navigate page '{page_name}': {e}")
            if "has been closed" not in str(e):
                raise e
            
            await self.relaunch_browser()
            return await self.create_or_navigate_page(page_name, url, open_mode, timeout, wait_until)


    async def create_or_navigate_page(self, page_name, url, open_mode, timeout, wait_until):
        if open_mode == "close" and page_name in self.pages and not self.pages[page_name].is_closed():
            await self.pages[page_name].close()

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

        try:
            if self._playwright:
                await self._playwright.stop()
        except Exception as e:
            print(f"[WARN] Failed to close Playwright: {e}")
