import os
from dotenv import load_dotenv
load_dotenv()

goto_url = os.getenv("GOTO_URL")
profile = os.getenv("BROWSER_PROFILE")
playwright_headless = True
max_retries = 15
retry_delay_sec = 5
interval_days = 2
