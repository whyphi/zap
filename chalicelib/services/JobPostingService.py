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
    
    def getJobs(self, urlStr) -> List:
        self.driver.get(urlStr)
    
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
            
            company = ""
            role = ""
            link = ""
            
            try:
                company = cols[0].find_element(By.TAG_NAME, "strong").find_element(By.TAG_NAME, "a").text
                prevRowCompany = company
            except NoSuchElementException:
                company = prevRowCompany
            
            try:
                role = cols[1].find_element(By.TAG_NAME, "strong").find_element(By.TAG_NAME, "a").text
                link = cols[1].find_element(By.TAG_NAME, "strong").find_element(By.TAG_NAME, "a").get_attribute("href")
            except:
                role = cols[1].text
            
            if link == "":
                link = cols[3].find_element(By.TAG_NAME, "a").get_attribute("href")
                
            newJob = {"company": company, 
                      "role": role,
                      "link": link,
                      "date": date}
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

if __name__ == "__main__":
    test_service = JobPostingService()
    links = [('Simplify (Tech)', 'https://github.com/SimplifyJobs/Summer2025-Internships/blob/dev/README.md'), 
             ('Cvrve (Tech)','https://github.com/cvrve/Summer2025-Internships/blob/dev/README.md'), 
             ('Jobright.ai (Consulting)','https://github.com/jobright-ai/2025-Consultant-Internship/blob/master/README.md'), 
             ('Jobright.ai (Marketing)','https://github.com/jobright-ai/2025-Marketing-Internship/blob/master/README.md')]
    
    for source, link in links:
        postings = test_service.getJobs(link)
        print(f"{source}:\n{postings}\n\n\n")