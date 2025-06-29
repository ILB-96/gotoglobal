import os
from pathlib import Path
import subprocess
from time import sleep
from playwright.async_api import BrowserContext, Page, Playwright, Error as PlaywrightError, Browser
from typing import Optional
import ctypes
from ctypes import wintypes, byref
from uuid import UUID

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
                self.browser = await self._playwright.chromium.connect_over_cdp('http://localhost:9222')
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
        else:
            browser = await self._playwright.chromium.launch(
                headless=self._headless)
            self.context: BrowserContext = await browser.new_context()

                
            
        self.pages: dict[str, Page] = {}
                
        return self
    

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
