from services import TinyDatabase
from playwright.sync_api import sync_playwright
from .late_alert import LateAlert

def setup_shared_resources(mode):
    db = TinyDatabase(
        {
            "goto": [
                "gotoDB.json",
                "reservation_id"
            ]
        }
    )
    return db


def start_task_thread(db):
    """Function to start a Playwright instance in a thread."""
    with sync_playwright() as playwright:
        LateAlert(db).start_requests(playwright)
        
        
def run(mode=0):
    db = setup_shared_resources(mode)
    start_task_thread(db)
