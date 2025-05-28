import os
import re
from time import sleep
import settings
from services import WebAccess, Log, TinyDatabase, QueryBuilder
import pyperclip
from datetime import datetime as dt, timedelta
from win11toast import toast

class BatteriesAlert:
    def __init__(self, db:TinyDatabase):
        self.db = db
        
    def start_requests(self, playwright):
        with WebAccess(playwright, settings.playwright_headless, str(settings.profile)) as web_access:
            web_access.start_context(str(settings.autotel_url), "")
            autotel_cars_url = str(settings.autotel_url) + r'/index.html#/cars/'
            web_access.pages[0].goto(autotel_cars_url)
            web_access.pages[0].locator("td").filter(has_text="AllAvailablePending").get_by_role("combobox").select_option("number:60")
            web_access.pages[0].get_by_role("cell", name="All").get_by_role("combobox").select_option("number:1")
            cars_rows = web_access.pages[0].locator('//tr[contains(@ng-repeat, "row in $data track by $index")]').all()
            
            for row in cars_rows:
                car_id = row.locator('//*[contains(@ng-click, "carsTableCtrl.showCarDetails(row)")]').text_content()
                car_battery = row.locator('td').filter(has_text='%').text_content()
                active_ride = row.locator('td').filter(has_text='ActiveRide').text_content()
                