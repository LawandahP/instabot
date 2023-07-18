import pickle
import time
import os
from typing import Any
from bs4 import BeautifulSoup
import openpyxl

import datetime
from colorama import Fore

from random import randint
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


class LinkedInBot():
    def __init__(self, username, password):
        self.browserProfile = Options()
        # self.browserProfile.add_argument("--headless")  # Run in headless mode
        self.browserProfile.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        self.browserProfile.add_argument("--disable-blink-features=AutomationControlled") 
        self.browserProfile.add_experimental_option("excludeSwitches", ["enable-automation"]) 
        self.browserProfile.add_experimental_option("useAutomationExtension", False) 
        self.browser = webdriver.Chrome(options=self.browserProfile)
        self.browser.maximize_window()

        self.username = username
        self.password = password
        self.cookies_file_path = "cookies_.pkl"
        self.max_retries = 15

        self.wait = WebDriverWait(self.browser, 2)

        self.error = Fore.RED
        self.success = Fore.GREEN
        self.info = Fore.CYAN

        self.errorIcon = "❌"
        self.successIcon = "✅"
        self.infoIcon = "ℹ️ "

        self.filename = ""

    def save_cookies(self):
        cookies = self.browser.get_cookies()
        pickle.dump(cookies, open(self.cookies_file_path, "wb"))

    def load_cookies(self):
        self.browser.get('https://www.linkedin.com/')

        with open(self.cookies_file_path, 'rb') as f:
            cookies = pickle.load(f)

        # Check if any cookies are expired
        now = datetime.datetime.now()
        expired_cookies = []
        for cookie in cookies:
            expiration = cookie.get('expiry')
            if expiration:
                expiration_date = datetime.datetime.fromtimestamp(expiration)
                if expiration_date < now:
                    expired_cookies.append(cookie)
                    print("Cookie has expired:", cookie)
                    os.remove(self.cookies_file_path)
                    return

        if expired_cookies:
            print("[*] One or more cookies have expired. Deleting the cookies file and restarting the login process.")
            os.remove(self.cookies_file_path)
            self.signIn()
        else:
            # Add the cookies to the browser instance
            for cookie in cookies:
                self.browser.add_cookie(cookie)
        # Refresh the page to apply the cookies
        self.browser.refresh()

    def signIn(self):
        # Check if cookies file exists
        
        retry_flag = False

        for retry in range(self.max_retries):
            try:
                if not os.path.exists(self.cookies_file_path):
                    self.browser.get('https://www.linkedin.com/')
                    time.sleep(2)
                    usernameInput = self.browser.find_element('css selector', 'input[name="session_key"]')
                    passwordInput = self.browser.find_element('css selector', 'input[name="session_password"]')
                    usernameInput.send_keys(self.username)
                    passwordInput.send_keys(self.password)
                    passwordInput.send_keys(Keys.ENTER)
                    time.sleep(getRandomTime())

                    try:
                        """Close Notifications"""
                        self.browser.find_element(By.XPATH, '//button[contains(text(), "Not Now")]').click()
                    except NoSuchElementException:
                        pass

                    # Save cookies
                    self.save_cookies()
                else:
                    # if previous logged in Load cookies from file
                    self.load_cookies()

                time.sleep(getRandomTime())

            except WebDriverException as e:
                print(self.error + f'{self.errorIcon} Retry {retry + 1} failed: {str(e)}')
                retry_flag = True
            
            if not retry_flag:
                break

            if retry == self.max_retries - 1:
                print(self.info + f'{self.infoIcon} Maximum retries exceeded. Exiting.')

    def getProfileDetails(self, profile_links=[]):
        profile_data = []
        for link in profile_links:
            self.browser.get(link)

            time.sleep(getRandomTime())

            name_xpath = '/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[1]/div[1]/h1'

            try:
                name = self.browser.find_element(By.XPATH, name_xpath)
                full_name = name.text
                time.sleep(getRandomTime())


                more_button = None

                while not more_button:
                    try:
                        more_button = self.browser.find_element(By.CSS_SELECTOR, "button.inline-show-more-text__button")
                    except NoSuchElementException:
                        # Scroll the page to continue searching for the button
                        self.browser.execute_script("window.scrollBy(0, window.innerHeight);")
                        time.sleep(getRandomTime())

                # more_button = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button.inline-show-more-text__button")))
                # actions = ActionChains(self.browser)
                # actions.move_to_element(more_button)
                # actions.perform()

                more_button.click()
                
                time.sleep(getRandomTime())
                
                about = self.browser.find_element(By.CSS_SELECTOR, "div.inline-show-more-text span.visually-hidden")
                about = about.text

                profile_data.append([
                    full_name,
                    about
                ])

            except NoSuchElementException as e:
                print(self.error + f"{self.errorIcon} An Error Occured:", e)

            self.writeDataToExcel(profile_data, full_name, ["Full Name", "About"])

    def writeDataToExcel(self, data, name, headers = []):
        workbook = openpyxl.Workbook()

        worksheet = workbook.active

        headers = headers
        worksheet.append(headers)
        worksheet.column_dimensions['A'].width = 30
        worksheet.column_dimensions['B'].width = 30



        for i, row in enumerate(data, start=1):
            cell = worksheet.cell(row=i, column=2)
            cell.alignment = cell.alignment.copy(wrapText=True)
            worksheet.append(row)

        self.filename = self.generate_file_name(name)

        workbook.save(self.filename)

    def generate_file_name(self, name):
        timestamp = int(time.time())
        filename = f"{name}_{timestamp}.xlsx"
        return filename

def getRandomTime():
    randTime = randint(3, 5)
    return randTime



bot = LinkedInBot("kairuthigithaiga@gmail.com", "@Sventeen18!")
bot.signIn() 

bot.getProfileDetails(['https://www.linkedin.com/in/githaiga-kairuthi/', ])