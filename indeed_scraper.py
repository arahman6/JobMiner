import os
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

# Set path to chromedriver as per your configuration
webdriver_service = Service(ChromeDriverManager().install())

# Choose Chrome Browser
driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

# Connect to MongoDB
client = MongoClient(MONGO_DB_URL)
db = client['job_miner']
collection = db['jobs_link']

# Define the base URL and number of pages to scrape
base_url = 'https://www.indeed.com/jobs?q=data+engineer&l=California'
num_pages = 10

for page in range(num_pages):
    url = f'{base_url}&start={page * 10}'
    driver.get(url)
    SleepHelper.random_sleep(12, 2)   # wait for the page to load

    # Find all job postings
    job_postings = driver.find_elements(By.CLASS_NAME, 'job_seen_beacon')

    # Extract information from each job posting
    for job in job_postings:
        try:
            # Click the job to view details
            job.click()
            SleepHelper.random_sleep(15, 3)  # wait for the details panel to load

            # Extract job title
            title_elem = job.find_element(By.CLASS_NAME, 'jobTitle')
            title = title_elem.text.strip() if title_elem else 'N/A'
            
            # Extract company name    
            company_elem = job.find_element(By.CSS_SELECTOR, "span[data-testid='company-name']")
            company = company_elem.text.strip() if company_elem else 'N/A'
            
            # Extract job location
            location_elem = job.find_element(By.CSS_SELECTOR, "div[data-testid='text-location']")
            location = location_elem.text.strip() if location_elem else 'N/A'
            
            # Extract job link
            joblink_elem = job.find_element(By.CLASS_NAME, 'jobTitle').find_element(By.CLASS_NAME, 'jcs-JobTitle').get_attribute('href')
            joblink = joblink_elem.strip() if joblink_elem else 'N/A'

            # Extract job details (e.g., salary, employment type, etc.)
            detail_sections = driver.find_elements(By.CLASS_NAME, 'jobsearch-JobDescriptionSection-sectionItem')
            details = {}
            for section in detail_sections:
                key_elem = section.find_element(By.CLASS_NAME, 'jobsearch-JobDescriptionSection-sectionItemKey')
                value_elem = section.find_element(By.CLASS_NAME, 'jobsearch-JobDescriptionSection-sectionItemValue')
                key = key_elem.text.strip() if key_elem else 'N/A'
                value = value_elem.text.strip() if value_elem else 'N/A'
                details[key] = value

            # Extract job description
            description_elem = driver.find_element(By.CLASS_NAME, 'jobsearch-JobComponent-description')
            description = description_elem.text.strip() if description_elem else 'N/A'
            
            # Print job information
            print(f'Job Title: {title}')
            print(f'Company: {company}')
            print(f'Location: {location}')
            print(f'Job Link: {joblink}')
            print(f'Details: {details}')
            print(f'Description: {description}')
            print('-' * 40)

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
        except Exception as e:
            print(f"Error processing job: {e}")
            continue

# Close the browser
driver.quit()
