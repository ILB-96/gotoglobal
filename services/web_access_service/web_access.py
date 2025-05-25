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

from services import Log


class WebAccess:
    """Provides access to web functionality."""

    def __init__(self, playwright: Playwright, headless=True, profile: str = None):
        """
        Initializes a WebAccess object.

        Parameters:
        - playwright (Playwright): The Playwright instance used to launch the browser.
        - headless (bool): Whether to run the browser in headless mode. Default is True.
        - profile (str): Path to a user data directory for persistent context. Optional.
        """
        edge_executable_path = Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")
        args = ["--profile-directory=Default"]
        
        
        if profile:
            self.profile = Path(profile)
            assert os.path.isdir(profile) or not os.path.exists(profile)

            self.context: BrowserContext = playwright.chromium.launch_persistent_context(
                user_data_dir=profile,
                headless=headless,
                executable_path=edge_executable_path,
                args=args,
            )
            self.browser = self.context.browser
        else:
            self.profile = None
            self.browser: Browser = playwright.chromium.launch(
                headless=headless,
                executable_path=edge_executable_path,
            )
            self.context: BrowserContext = self.browser.new_context()

        self.pages: list[Page] = [self.context.pages[0] if self.context.pages else self.context.new_page()]

    def start_context(
        self, url: str, ignore="**/*.{png,jpg,jpeg,css,svg}", timeout=45000
    ):
        # Persistent context: don't recreate context

        if not self.profile:
            self.context = self.browser.new_context()
            self.pages: list[Page] = [self.context.new_page()]
        if ignore:
            self.context.route(ignore, lambda route: route.abort())
        self.pages[-1].goto(url, timeout=timeout, wait_until="networkidle")

    def new_tab(self, url: str, timeout=45000):
        """Opens a new tab in the browser and navigates to the specified URL.

        Args:
            url (str): The URL to navigate to.
            timeout (int, optional): The maximum time to wait for the page to load, in milliseconds. Defaults to 45000.

        Returns:
            New tab index (int): The index of the newly opened tab in the pages list.
        """
        self.pages.append(self.context.new_page())
        self.pages[-1].goto(url, timeout=timeout, wait_until="networkidle")
        return len(self.pages) - 1
    
    @staticmethod
    def expect_text(locator: Locator, default=""):
        try:
            return locator.inner_text()
        except (KeyboardInterrupt, TargetClosedError):
            raise KeyboardInterrupt("User Keyboard interrupt.")
        except Exception:
            return default

    @staticmethod
    def expect_click(
        element: Locator,
        expect_visible=False,
    ):
        try:
            if expect_visible:
                expect(element).to_be_visible(timeout=1000)
            element.click()
            return True
        except (KeyboardInterrupt, TargetClosedError):
            raise KeyboardInterrupt("User Keyboard interrupt.")
        except Exception:
            return False

    def click_by_text(
        self,
        element_type: str,
        text: str,
        label: str = "text()",
    ):
        return self.expect_click(
            self.page.locator(
                f"xpath=//{element_type}[normalize-space({label})='{text}']"
            )
        )

    def open_all_dropdowns(self, xpath: str):
        dropdown_toggles = self.page.locator(xpath).all()
        for toggle in dropdown_toggles:
            self.page.wait_for_timeout(timeout=100)
            self.expect_click(toggle, True)
    
    def get_download(
        self,
        pdf_link: Locator,
        name: str,
        folder: str,
        ext="pdf",
        timeout=30000,
    ):
        path = os.path.join(folder, f"{name}.{ext}")

        if os.path.isfile(path):
            return path

        try:
            with self.page.expect_download(timeout=timeout) as download_info:
                if not self.expect_click(pdf_link.nth(0), True):
                    with open("skipped_files.log", "a") as f:
                        f.write(f"{dt.now()}\nURL: {self.page.url}\nPATH:{path}\n\n")
                    return None

            download = download_info.value
            download.save_as(path=path)
            if download.path():
                return path
        except (KeyboardInterrupt, TargetClosedError):
            raise KeyboardInterrupt("User Keyboard interrupt.")
        except Exception as e:
            with open("skipped_files.log", "a") as f:
                f.write(
                    f"{dt.now()}\nURL: {self.page.url}\nPATH:{path}\n{e.__class__}: {e}\n\n"
                )

    def open_date_picker(self, input_selector: str):
        self.page.locator(input_selector).click()
        self.page.get_by_role("button", name=str(dt.now().year)).nth(0).click()

    def select_date_picker_year(
        self,
        year: str,
        years_range_selector: str,
        range_prev_selector: str,
        range_next_selector: str,
    ):
        cal_year_range = self.page.locator(years_range_selector).inner_text().split("-")
        start, end = (
            int(cal_year_range[0].strip()) > int(year),
            int(year) > int(cal_year_range[1].strip()),
        )
        while start or end:
            if start:
                self.page.locator(range_prev_selector).click()
            else:
                self.page.locator(range_next_selector).click()

            cal_year_range = (
                self.page.locator("//span[contains(@class, 'p-datepicker-decade')]")
                .inner_text()
                .split("-")
            )
            start, end = (
                int(cal_year_range[0].strip()) > int(year),
                int(year) > int(cal_year_range[1].strip()),
            )
        self.page.get_by_text(year, exact=True).click()

    def select_date_picker_month(
        self,
        month: str,
        months_selector: str,
    ):
        self.page.locator(months_selector).nth(int(month) - 1).click()

    def select_date_picker_day(self, day: str, excluded_elements_classes: str):
        self.page.locator(
            f"//td[not(contains(@class, '{excluded_elements_classes}'))]/span[normalize-space(text())='{day}']"
        ).click()

    def click_until_btn_invisible(self, button_selector: str, timeout: int = 30000):
        """Clicks on a button repeatedly until it becomes invisible.

        Args:
            button_selector (str): The CSS or XPATH selector of the button to click.
            timeout (int, optional): The maximum time to wait for the button to become invisible, in milliseconds.
            Defaults to 15000.

        Returns:
            None
        """
        while True:
            try:
                button = self.page.locator(button_selector)
                expect(button).to_be_visible(timeout=timeout)
                button.click(timeout=timeout)
            except (KeyboardInterrupt, TargetClosedError):
                raise KeyboardInterrupt("User Keyboard interrupt.")
            except Exception:
                break

    def scroll_until_end_of_page(
        self, scrollable_div_selector: str, step: int = 100, timeout: int = 500
    ):
        """Scrolls the page until the end of the scrollable div.

        Args:
            scrollable_div_selector (str): The CSS or XPATH selector of the scrollable div element.
            step (int, optional): The amount of pixels to scroll vertically in each step. Defaults to 100.
            timeout (int, optional): The timeout in milliseconds between each scroll step. Defaults to 500.
        """
        scrollable_div = self.page.locator(scrollable_div_selector)
        last_scroll_height = self.page.evaluate(
            "element => element.scrollHeight", scrollable_div
        )

        while True:
            self.page.evaluate(
                f"element => element.scrollBy(0, {step})", scrollable_div
            )
            self.page.wait_for_timeout(timeout=timeout)

            new_scroll_height = self.page.evaluate(
                "element => element.scrollHeight", scrollable_div
            )
            current_scroll_position = self.page.evaluate(
                "element => element.scrollTop", scrollable_div
            )
            if not (box := scrollable_div.bounding_box()):
                raise ValueError("Could not get bounding box of scrollable div.")

            if current_scroll_position + box["height"] >= last_scroll_height:
                break

            last_scroll_height = new_scroll_height
            
    def query_locator_all(self, locator: str) -> Generator[Locator, None, None]:

        for locator in self.page.locator(locator).all():
            try:
                yield locator
            except (KeyboardInterrupt, TargetClosedError):
                raise KeyboardInterrupt("User Keyboard interrupt.")
            except Exception as e:
                Log.error(f"Error in query_locator_all: {e}")
                continue
            
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
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
        except Exception as e:
            pass


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
