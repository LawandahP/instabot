import pickle
import time
import os
import requests
import openpyxl

from random import randint
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

class ClinicsBot():
    def __init__(self):
        self.browserProfile = Options()
        # self.browserProfile.add_argument("--headless")  # Run in headless mode
        self.browserProfile.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        self.browserProfile.add_argument("--disable-blink-features=AutomationControlled") 
        self.browserProfile.add_experimental_option("excludeSwitches", ["enable-automation"]) 
        self.browserProfile.add_experimental_option("useAutomationExtension", False) 
        self.browser = webdriver.Chrome(options=self.browserProfile)

        self.wait = WebDriverWait(self.browser, 2)
        self.max_retries = 15

    def writeDataToExcel(self, data):
        workbook = openpyxl.Workbook()

        worksheet = workbook.active
        headers = ["Name", "Telephone", "Address", "Operating Hours"]
        worksheet.append(headers)

        for row in data:
            worksheet.append(row)

        workbook.save("clinics_data.xlsx")

    def getClinicsPage(self):
        self.browser.get("https://www.hcidirectory.gov.sg/hcidirectory/clinic.do?task=loadRegion")


        map_element = self.browser.find_element(By.ID, 'regionMap')
        area_elements = map_element.find_elements(By.TAG_NAME, 'area')

        for area_element in area_elements:
            time.sleep(1)
            area_element.click()

        search_button = self.browser.find_element(By.NAME, 'Search')

        # Click on the input element
        search_button.click()

        time.sleep(3.5)

    def scrapClinics(self):
        page_source = self.browser.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        result_containers = soup.find_all('div', class_='result_container')

        data = []
        for container in result_containers:
            try:
                name = container.find('span', class_='name').a.text.strip()
            except AttributeError:
                name = "N/A"
                
            try:
                tel_span = container.find('span', class_='tel')
                tel = tel_span.find('a', class_='contact_mobile').text.strip() if tel_span.find('a', class_='contact_mobile') else "N/A"
                
            except AttributeError:
                tel = "N/A"
                
            try:
                address = container.find('span', class_='add').text.replace('\t', '').replace('\n', '').replace('  ', '').strip()
            except AttributeError:
                address = "N/A"
                
            try:
                operating_hours = container.find('span', class_='time').text.strip()
            except AttributeError:
                operating_hours = "N/A"

            data.append([name, tel, address, operating_hours])

        # self.writeDataToExcel(data)
        return data
    
    def clickPagination(self):
        data = self.scrapClinics()

        time.sleep(10)

        # while True:
        page_control = self.browser.find_element(By.ID, 'PageControl')
        pagination_elements = page_control.find_elements(By.CSS_SELECTOR, 'ul li:not(.selected) a.pagelinks')

        pagination_elements_list = []
        

        # if not pagination_elements:
        #     break  # Exit the loop if no more pagination elements are found

        for element in pagination_elements:
            pagination_elements_list.append(element)
        
        print(pagination_elements_list)

        with open("pyth.py", "w") as f:
            f.write('\n'.join(map(str, pagination_elements)))
        print("pagination elements =============>>>>>", len(pagination_elements))
        
        for element in pagination_elements_list:
            try:
                element.click()
                pagination_elements_list.remove(element)
                print(pagination_elements_list)
                time.sleep(5)
                data += self.scrapClinics()
                self.writeDataToExcel(data)
            except StaleElementReferenceException:
                # If the element becomes stale, break the inner loop and re-fetch the pagination elements
                break
        return

            



bot = ClinicsBot()
bot.getClinicsPage()
bot.clickPagination()


