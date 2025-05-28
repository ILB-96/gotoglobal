from services import WebAccess
import settings
from src.goto.late_alert.late_alert import LateAlert
from playwright.sync_api import sync_playwright




"""Function to start a Playwright instance in a thread."""
with sync_playwright() as playwright:
    with WebAccess(playwright, settings.playwright_headless, str(settings.profile)) as web_access:
        web_access.start_context(str(settings.goto_url), "")
        LateAlert(None)._fetch_and_store_ride_times(
            "60842163",
            web_access
        )