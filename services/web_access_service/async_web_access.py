import os
from pathlib import Path
from playwright.async_api import BrowserContext, Page, Playwright, Error as PlaywrightError
from typing import Optional

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
        playwright: Playwright,                  # the result of `async with async_playwright()`
        headless: bool = True,
        browser_name: Optional[Path] = 'edge',
        profile: Optional[str] = "Default",
    ):
        self._playwright = playwright
        self._headless = headless
        self._browser_name = browser_name
        self._profile = profile or None
        self.context: Optional[BrowserContext] = None
        self.pages: dict[str, Page] = {}

    async def __aenter__(self):
        # if self._browser_name == 'edge':
        #     BROWSER_PATH = Path(
        #         "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
        #     )
        # elif self._browser_name == 'chrome':
        #     BROWSER_PATH = Path(
        #         "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"
        #     )
        if self._profile:
            browser = await self._playwright.chromium.connect_over_cdp('http://localhost:9222')
            self.context = browser.contexts[0] if browser.contexts else await browser.new_context()
            # if self._browser_name == 'edge':
            #     user_data_dir = (
            #         Path.home()
            #         / "AppData"
            #         / "Local"
            #         / "Microsoft"
            #         / "Edge"
            #         / "User Data"
            #         / self._profile
            #     )
            # else:
            #     user_data_dir = (
            #         Path.home()
            #         / "AppData"
            #         / "Local"
            #         / "Google"
            #         / "Chrome"
            #         / "User Data"
            #         / self._profile
            #     )

        #     assert os.path.exists(user_data_dir)
        #     try:
        #         self.context = await self._playwright.chromium.launch_persistent_context(
        #             user_data_dir=user_data_dir.parent,
        #             headless=self._headless,
        #             executable_path=BROWSER_PATH,
        #             args=["--profile-directory=" + self._profile],
        #             no_viewport=True
        #         )
        #     except PlaywrightError as e:
        #         # Fallback to a fresh context if persistent failed (e.g. profile in use)
        #         print(f"[AsyncWebAccess] persistent context failed: {e!r}\n– falling back to fresh context")
                
        # else:
        #     browser = await self._playwright.chromium.launch(
        #         headless=self._headless,
        #         executable_path=BROWSER_PATH,
        #     )
        #     self.context = await browser.new_context()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.context:
            await self.context.close()
        # don't suppress exceptions
        return False

    async def start_context(self, ignore_patterns: str = "**/*.{png,jpg,jpeg,css,svg}"):
        if not self.context:
            raise RuntimeError("Context not initialized")
        await self.context.route(ignore_patterns, lambda route: route.abort())

    async def create_pages(self, pages: dict[str, str]):
        if not self.context:
            raise RuntimeError("Context not initialized")
        for name, url in pages.items():
            await self.create_new_page(name, url)

        self.pages['blank'] = await self.create_new_page('blank', 'about:blank', open_mode='reuse')

    async def create_new_page(
        self,
        page_name: str,
        url: str,
        open_mode: str = "close",
        timeout: int = 45_000,
        wait_until: str = "networkidle",
    ) -> Page:
        if open_mode == "close" and page_name in self.pages:
            old = self.pages[page_name]
            if not old.is_closed():
                await old.close()

        if page_name not in self.pages or self.pages[page_name].is_closed():
            page = await self.context.new_page()
            self.pages[page_name] = page
        elif open_mode == "reuse" and self.pages[page_name].url.startswith(url):
            return self.pages[page_name]
        else:
            page = self.pages[page_name]

        await page.goto(url, timeout=timeout, wait_until=wait_until)
        return page

    async def cleanup(self):
        if self.context:
            await self.context.close()
