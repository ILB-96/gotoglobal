import os
import re
from time import sleep
import settings
from services import WebAccess, Log, TinyDatabase, QueryBuilder
import pyperclip
from datetime import datetime as dt, timedelta
from win11toast import toast

from src.shared import PointerLocation

class BatteriesAlert:
    def __init__(self, db:TinyDatabase, show_toast, gui_table_row, web_access: WebAccess, pointer: PointerLocation):
        self.db = db
        self.show_toast = show_toast
        self.gui_table_row = gui_table_row
        self.web_access = web_access
        self.pointer = pointer
        
    def start_requests(self):
        autotel_cars_url = r'https://prodautotelbo.gototech.co/index.html#/cars'
        page = self.web_access.create_new_page("autotel_bo", autotel_cars_url, "update")
        self.web_access.pages['pointer'].reload()
        sleep(5)
        select_elements = page.locator("select").all()
        select_elements[0].select_option("number:60")
        sleep(5)
        select_elements[1].select_option("number:1")
        sleep(5)
        cars_rows = page.locator('//tr[contains(@ng-repeat, "row in $data track by $index")]').all()

        rows = []
        for row in cars_rows:
            car_id = str(row.locator('//*[contains(@ng-click, "carsTableCtrl.showCarDetails(row)")]').text_content()).strip()
            car_battery = str(row.locator('td').filter(has_text='%').text_content()).strip()
            active_ride = str(row.locator("//*[contains(@ng-if, \"::$root.matchProject('ATL')||($root.matchProject('E2E'))\")][4]").text_content()).strip()
            location = self.pointer.search_location(car_id.replace("-", ""))
            
            rows.append([car_id, car_battery, active_ride, location])
            
        self.gui_table_row(rows)
