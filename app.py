from services import Scheduler
import settings
from src.goto import late_alert

def verify_environment():
    """
    This function verifies if the environment is set up correctly.
    It checks for the presence of required environment variables.
    """
    if not settings.goto_url:
        raise ValueError("GOTO_URL environment variable is not set.")
    if not settings.profile:
        raise ValueError("BROWSER_PROFILE environment variable is not set.")
    
    
if __name__ == "__main__":
    tasks = [(late_alert.run, 0)]
    verify_environment()
    scheduler = Scheduler( interval_minutes=15, tasks=tasks)
    scheduler.start()
