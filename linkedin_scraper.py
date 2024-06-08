#%%
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from pymongo import MongoClient
from dotenv import load_dotenv
from sleep_helper import SleepHelper
from web_scraper_helper import WebScraperHelper

# Load environment variables from .env file
load_dotenv()
MONGO_DB_URL = os.getenv("MONGO_DB_URL")


# Setup Chrome options
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Ensure GUI is off
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--always-enable-hdcp")


# Set path to chromedriver as per your configuration
webdriver_service = Service(ChromeDriverManager().install())

# Choose Chrome Browser
# driver = webdriver.Chrome( options=chrome_options)
driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

# Connect to MongoDB
client = MongoClient(MONGO_DB_URL)
db = client['job_miner']
collection = db['jobs_circular']

# Define the base URL and number of pages to scrape
base_url = 'https://www.linkedin.com/jobs/search/?keywords=data%20engineer&location=California%2C%20United%20States'
num_pages = 2

SleepHelper.random_sleep(15, 3)

for page in range(num_pages):
    url = f'{base_url}&start={page * 25}'
    driver.get(url)
    SleepHelper.random_sleep(12, 2)  # wait for the page to load

    # Find all job postings
    job_postings = driver.find_element(By.CLASS_NAME, 'jobs-search__results-list').find_elements(By.CLASS_NAME, 'base-card')

    # Extract information from each job posting
    for job in job_postings:
        # Extract job title
        title = WebScraperHelper.safe_find_text(job, By.CSS_SELECTOR, 'h3.base-search-card__title')

        # Extract company name
        company = WebScraperHelper.safe_find_text(job, By.CSS_SELECTOR, 'h4.base-search-card__subtitle')

        # Extract job location
        location = WebScraperHelper.safe_find_text(job, By.CSS_SELECTOR, 'span.job-search-card__location')

        # Extract job link
        joblink = WebScraperHelper.safe_find_link(job, By.CSS_SELECTOR, 'a.base-card__full-link')

        # Click on the job link to get detailed information
        WebScraperHelper.safe_find_click(job, By.CSS_SELECTOR, 'a.base-card__full-link')

        SleepHelper.random_sleep(15, 3)


        # Extract job description
        description = WebScraperHelper.safe_find_text(driver, By.CSS_SELECTOR, 'div.description__text')

        # Extract job details (e.g., salary, employment type, etc.)
        details = {}

        key = WebScraperHelper.safe_find_text_by_selectors(driver,[(By.CSS_SELECTOR, 'div.compensation__salary-range'),(By.CSS_SELECTOR, 'h3.compensation__heading')])
        value = WebScraperHelper.safe_find_text_by_selectors(driver, [(By.CSS_SELECTOR, 'div.compensation__salary-range'),(By.CSS_SELECTOR, 'div.compensation__salary')])
        details[key] = value

        detail_sections = driver.find_elements(By.CSS_SELECTOR, 'li.description__job-criteria-item')

        for section in detail_sections:
            key = WebScraperHelper.safe_find_text(section, By.CSS_SELECTOR, 'h3.description__job-criteria-subheader')
            value = WebScraperHelper.safe_find_text(section, By.CSS_SELECTOR, 'span.description__job-criteria-text')
            details[key] = value

        # Create a dictionary to store the job data
        job_data = {
            'source': 'linkedin',
            'title': title,
            'company': company,
            'location': location,
            'job_link': joblink,
            'details': details,
            'description': description
        }

        # Insert the job data into MongoDB
        collection.insert_one(job_data)


driver.quit()
