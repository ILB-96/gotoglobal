import os
from dotenv import load_dotenv
load_dotenv()

user_email = os.getenv("EMAIL")
user_password = os.getenv("PASSWORD")
goto_url = os.getenv("GOTO_URL")
profile = os.getenv("BROWSER_PROFILE")
playwright_headless = False
max_retries = 15
retry_delay_sec = 5
interval_days = 2
