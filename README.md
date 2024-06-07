# MultiJobScraper

## Overview
MultiJobScraper is a Python project to scrape job listings from multiple job portals like LinkedIn and Indeed.

## Setup
1. Clone the repository.
2. Navigate to the project directory.
3. Create a virtual environment and activate it:
    ```sh
    python -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    ```
4. Install the required libraries:
    ```sh
    pip install -r requirements.txt
    ```

## Usage
- Update the `linkedin_url` and `indeed_url` in `main.py` with the actual job search URLs.
- Run the scraper:
    ```sh
    python main.py
    ```
- The scraped job data will be saved to `linkedin_jobs.json` and `indeed_jobs.json`.

## Extending the Project
To add more job portals, create a new scraper class extending `BaseScraper` and implement the required methods.
