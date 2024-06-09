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

# Set path to chromedriver as per your configuration
webdriver_service = Service(ChromeDriverManager().install())

# Choose Chrome Browser
driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

# Connect to MongoDB
client = MongoClient(MONGO_DB_URL)
db = client['job_miner']
collection = db['jobs_circular']


# Generate the base_url

with open('./data/job_search_keyword.json') as f:
    job_data = json.load(f)

base_url = 'https://www.indeed.com/jobs?q={job_title}&l=California'

# Function to generate URLs
def generate_urls(job_data):
    urls = []
    for category, job_titles in job_data.items():
        for job_title in job_titles:
            job_title_query = job_title.replace(' ', '+')
            urls.append(base_url.format(job_title=job_title_query))
    return urls

# Generate URLs
job_urls = generate_urls(job_data)

# Print the URLs
for url in job_urls:
    print(url)




# Define the base URL and number of pages to scrape
# base_url = 'https://www.indeed.com/jobs?q=data+engineer&l=California'
num_pages = 2

SleepHelper.random_sleep(15, 3)
for job_url in job_urls:
    for page in range(num_pages):
        url = f'{job_url}&start={page * 10}'
        driver.get(url)
        SleepHelper.random_sleep(12, 2)   # wait for the page to load

        # Find all job postings
        job_postings = driver.find_elements(By.CLASS_NAME, 'job_seen_beacon')

        # Extract information from each job posting
        for job in job_postings:
            # Click the job to view details
            job.click()
            SleepHelper.random_sleep(15, 3)  # wait for the details panel to load

            # Extract job title
            title = WebScraperHelper.safe_find_text(job, By.CLASS_NAME, 'jobTitle')

            # Extract company name
            company = WebScraperHelper.safe_find_text(job, By.CSS_SELECTOR, "span[data-testid='company-name']")

            # Extract job location
            location = WebScraperHelper.safe_find_text(job, By.CSS_SELECTOR, "div[data-testid='text-location']")

            # Extract job link
            joblink = WebScraperHelper.safe_find_link_by_selectors(job, [(By.CLASS_NAME, 'jobTitle'),(By.CLASS_NAME, 'jcs-JobTitle')])

            # Extract job details (e.g., salary, employment type, etc.)
            details = {}

            details['estimated salary'] = WebScraperHelper.safe_find_text_by_selectors(driver, [(By.CSS_SELECTOR, 'div[data-testid="jobsearch-OtherJobDetailsContainer"]'),(By.CSS_SELECTOR, 'div[id="salaryInfoAndJobType"]')])

            description = WebScraperHelper.safe_find_text(driver, By.CLASS_NAME, 'jobsearch-JobComponent-description')

            # Create a dictionary to store the job data
            job_data = {
                'source': 'indeed',
                'title': title,
                'company': company,
                'location': location,
                'job_link': joblink,
                'details': details,
                'description': description
            }

            # Insert the job data into MongoDB
            collection.insert_one(job_data)

# Close the browser
driver.quit()
