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
collection = db['jobs_linkedin']

# Define the base URL and number of pages to scrape
base_url = 'https://www.linkedin.com/jobs/search/?keywords=data%20engineer&location=California%2C%20United%20States'
num_pages = 2

for page in range(num_pages):
    url = f'{base_url}&start={page * 25}'
    driver.get(url)
    SleepHelper.random_sleep(12, 2)  # wait for the page to load

    # Find all job postings
    job_postings = driver.find_element(By.CLASS_NAME, 'jobs-search__results-list').find_elements(By.CLASS_NAME, 'base-card')

    # Extract information from each job posting
    for job in job_postings:
        try:
            # Extract job title
            title_elem = job.find_element(By.CSS_SELECTOR, 'h3.base-search-card__title')
            title = title_elem.text.strip() if title_elem else 'N/A'

            # Extract company name    
            company_elem = job.find_element(By.CSS_SELECTOR, 'h4.base-search-card__subtitle')
            company = company_elem.text.strip() if company_elem else 'N/A'

            # Extract job location
            location_elem = job.find_element(By.CSS_SELECTOR, 'span.job-search-card__location')
            location = location_elem.text.strip() if location_elem else 'N/A'

            # Extract job link
            joblink_elem = job.find_element(By.CSS_SELECTOR, 'a.base-card__full-link')
            joblink = joblink_elem.get_attribute('href').strip() if joblink_elem else 'N/A'

            # Click on the job link to get detailed information
            joblink_elem.click()
            SleepHelper.random_sleep(15, 3)  # wait for the job detail page to load


            # Extract job description
            description_elem = driver.find_element(By.CSS_SELECTOR, 'div.description__text')
            description = description_elem.text.strip() if description_elem else 'N/A'

            # Extract job details (e.g., salary, employment type, etc.)
            detail_sections = driver.find_elements(By.CSS_SELECTOR, 'li.description__job-criteria-item')
            details = {}
            
            key_elem = driver.find_element(By.CSS_SELECTOR, 'div.compensation__salary-range').find_element(By.CSS_SELECTOR, 'h3.compensation__heading')
            value_elem = driver.find_element(By.CSS_SELECTOR, 'div.compensation__salary-range').find_element(By.CSS_SELECTOR, 'div.compensation__salary')
            key = key_elem.text.strip() if key_elem else 'N/A'
            value = value_elem.text.strip() if value_elem else 'N/A'
            details[key] = value
            
            for section in detail_sections:
                key_elem = section.find_element(By.CSS_SELECTOR, 'h3.description__job-criteria-subheader')
                value_elem = section.find_element(By.CSS_SELECTOR, 'span.description__job-criteria-text')
                key = key_elem.text.strip() if key_elem else 'N/A'
                value = value_elem.text.strip() if value_elem else 'N/A'
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
            
            # print(json.dumps(job_data, indent=4))
            # print('-' * 40)
            
            # Insert the job data into MongoDB
            collection.insert_one(job_data)

            # # Close the job detail window and switch back to the main window
            # driver.close()
            # driver.switch_to.window(driver.window_handles[0])

        except Exception as e:
            print(f"Error processing job: {e}")
            continue

driver.quit()
