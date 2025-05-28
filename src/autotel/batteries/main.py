from services import TinyDatabase
from playwright.sync_api import sync_playwright
from .batteries import BatteriesAlert

def setup_shared_resources(mode):
    db = TinyDatabase(
        {
            "autotel": [
                "autotelDB.json",
                "ride_id"
            ]
        }
    )
    return db


def start_task_thread(db):
    """Function to start a Playwright instance in a thread."""
    with sync_playwright() as playwright:
        BatteriesAlert(db).start_requests(playwright)
        
        
def run(mode=0):
    db = setup_shared_resources(mode)
    start_task_thread(db)
