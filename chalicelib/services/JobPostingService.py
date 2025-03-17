from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
from typing import List

class JobPostingService:
    def __init__(self):
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run Chrome in headless mode
        options.add_argument("--disable-gpu")  # Necessary for some environments
        options.add_argument("--no-sandbox")  # Good practice for running in Docker/Linux
        webDriver = webdriver.Chrome(service=service, options=options)
        
        self.driver = webDriver
    
    def getTechJobs(self) -> List:
        page_url = "https://github.com/SimplifyJobs/Summer2025-Internships/blob/dev/README.md"
        self.driver.get(page_url)
    
        table = self.driver.find_element(By.TAG_NAME, "table")
        body = table.find_element(By.TAG_NAME, "tbody")
        rows = body.find_elements(By.TAG_NAME, "tr")
        
        prevRowCompany = ""
        jobs = []
        for row in rows:
            cols = row.find_elements(By.XPATH, "td")
            date = cols[-1].text
            if (self.isMoreThanOneWeekAgo(date)):
                break
            
            try:
                company = cols[0].find_element(By.TAG_NAME, "strong").find_element(By.TAG_NAME, "a").text
                prevRowCompany = company
            except NoSuchElementException:
                company = prevRowCompany
            
            role = cols[1].text
            link = cols[3].find_element(By.TAG_NAME, "a").get_attribute("href")
            
            newJob = [company, 
                      role,
                      link,
                      date]
            jobs.append(newJob)
        
        return jobs
    
    def isMoreThanOneWeekAgo(self, dateStr: str) -> bool:
        current_year = datetime.today().year
        today = datetime.today()
        date_obj = datetime.strptime(f"{dateStr} {current_year}", "%b %d %Y")
        one_week_ago = today - timedelta(days=8)
        if date_obj < one_week_ago:
            return True
        return False
    
job_posting_service = JobPostingService()