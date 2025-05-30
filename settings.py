import os
from dotenv import load_dotenv
load_dotenv()
app_icon = 'c2gFav.ico'
goto_url = os.getenv("GOTO_URL")
autotel_url = os.getenv("AUTOTEL_URL")
profile = os.getenv("BROWSER_PROFILE")
private_profile = os.getenv("PRIVATE_PROFILE")
playwright_headless = False
max_retries = 15
retry_delay_sec = 5
interval_days = 2
