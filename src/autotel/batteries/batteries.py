import os
import re
from time import sleep
import settings
from services import WebAccess, Log, TinyDatabase, QueryBuilder
import pyperclip
from datetime import datetime as dt, timedelta
from win11toast import toast

class BatteriesAlert:
    def __init__(self, db:TinyDatabase, show_toast, gui_table_row, web_access: WebAccess):
        self.db = db
        self.show_toast = show_toast
        self.gui_table_row = gui_table_row
        self.web_access = web_access
        
    def start_requests(self):
        autotel_cars_url = r'https://prodautotelbo.gototech.co/index.html#/cars'
        page = self.web_access.create_new_page("autotel_bo", autotel_cars_url, "update")
        sleep(5)
        select_elements = page.locator("select").all()
        select_elements[0].select_option("number:60")
        sleep(5)
        select_elements[1].select_option("number:1")
        sleep(5)
        cars_rows = page.locator('//tr[contains(@ng-repeat, "row in $data track by $index")]').all()
        # self.gui_table_row.clear_table()
        rows = []
        for row in cars_rows:
            car_id = str(row.locator('//*[contains(@ng-click, "carsTableCtrl.showCarDetails(row)")]').text_content()).strip()
            car_battery = str(row.locator('td').filter(has_text='%').text_content()).strip()
            active_ride = str(row.locator("//*[contains(@ng-if, \"::$root.matchProject('ATL')||($root.matchProject('E2E'))\")][4]").text_content()).strip()
            rows.append([active_ride, car_id, car_battery, ''])
        self.gui_table_row(rows)
        # self.gui_table.set_last_updated(dt.now().strftime("%H:%M"))
