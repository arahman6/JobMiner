import os
from selenium.common.exceptions import NoSuchElementException
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import inspect

# MongoDB connection setup
load_dotenv()
MONGO_DB_URL = os.getenv("MONGO_DB_URL")
client = MongoClient(MONGO_DB_URL)
db = client['job_miner']
log_collection = db['scraper_logs']


class WebScraperHelper:

    @staticmethod
    def log_exception(e, value):
        frame = inspect.currentframe().f_back.f_back
        filename = inspect.getframeinfo(frame).filename
        line_number = inspect.getframeinfo(frame).lineno

        # Log the exception to the database
        log_entry = {
            "datetime": datetime.now(),
            "filename": filename,
            "line_number": line_number,
            "value": value,
            "exception": str(e)
        }
        log_collection.insert_one(log_entry)


    @staticmethod
    def safe_find_text(driver, by, value, default='N/A'):
        try:
            element = driver.find_element(by, value)
            return element.text.strip()
        except NoSuchElementException as e:
            WebScraperHelper.log_exception(e, value)
            return default

    @staticmethod
    def safe_find_link(driver, by, value, default='N/A'):
        try:
            element = driver.find_element(by, value)
            return element.get_attribute('href').strip()
        except NoSuchElementException as e:
            WebScraperHelper.log_exception(e, value)
            return default

    @staticmethod
    def safe_find_click(driver, by, value):
        try:
            element = driver.find_element(by, value)
            return element.click()
        except NoSuchElementException as e:
            WebScraperHelper.log_exception(e, value)
            print(e)

    @staticmethod
    def safe_find_text_by_selectors(driver, selectors, default='N/A'):
        element = driver
        try:
            for by, value in selectors:
                element = element.find_element(by, value)
            return element.text.strip()
        except NoSuchElementException as e:
            WebScraperHelper.log_exception(e, selectors)
            return default

    @staticmethod
    def safe_find_link_by_selectors(driver, selectors, default='N/A'):
        element = driver
        try:
            for by, value in selectors:
                element = element.find_element(by, value)
            return element.get_attribute('href').strip()
        except NoSuchElementException as e:
            WebScraperHelper.log_exception(e, selectors)
            return default