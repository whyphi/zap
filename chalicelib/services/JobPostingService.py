from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from chalicelib.modules.google_sheets import GoogleSheetsModule
from datetime import datetime, timedelta
from typing import List, Dict
import re

class JobPostingService:
    def __init__(self):
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run Chrome in headless mode
        options.add_argument("--disable-gpu")  # Necessary for some environments
        options.add_argument("--no-sandbox")  # Good practice for running in Docker/Linux
        webDriver = webdriver.Chrome(service=service, options=options)
        self.driver = webDriver
        self.gs = GoogleSheetsModule()
    
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
            except NoSuchElementException:
                role = cols[1].text
            
            if link == "":
                link = cols[3].find_element(By.TAG_NAME, "a").get_attribute("href")
                
            newJob = {"company": company, 
                      "role": role,
                      "link": link,
                      "date": date}
            jobs.append(newJob)
        
        return jobs
    
    def getFinanceJobs(self) -> List[Dict]:
        JOBS_SHEET_ID = "15za1luZR08YmmBIFOAk6-GJB3T22StEuiZgFFuJeKW0"
        try:
            response = self.gs.get_all_cells(JOBS_SHEET_ID, "2027 Opportunities Tracker", "FORMULA")
            if not response.get("values"):
                return []
            
            # 2. Separate headers from rows
            headers = response["values"][5]
            rows = response["values"][6:31]
            
            # 3. Find the column indices for the columns we want
            company_idx = headers.index("Company")
            opp_idx = headers.index("Opportunity")
            link_idx = headers.index("Link")
            
            deadline_idxs = [i for i, header in enumerate(headers) if header == "Deadline"]
            if len(deadline_idxs) > 1:
                deadline_idx = deadline_idxs[1]
            else:
                deadline_idx = deadline_idxs[0]
            
            # 4. Loop through rows and extract only the columns we want
            job_listings = []
            hyperlink_regex = r'=HYPERLINK\("(.*?)","(.*?)"\)'
            for row in rows:
                raw_link = row[link_idx]
                # Use regex to extract the hyperlink URL.
                match = re.match(hyperlink_regex, raw_link)
                if not match:
                    # Skip this row if no match is found.
                    continue
                hyperlink_url = match.group(1)
                    
                raw_date = row[deadline_idx]
                date_str = self._convert_serial_to_date(raw_date)
                
                job = {
                    "company": row[company_idx],
                    "role": row[opp_idx],
                    "link": hyperlink_url,
                    "date": date_str
                }
                job_listings.append(job)
            
            return job_listings

        except Exception as e:
            print(e)
            return []
        
    def _convert_serial_to_date(self, raw_date) -> str:
        """
        Converts a serial date (as returned by Google Sheets when using FORMULA mode)
        into a human-readable string (e.g. "Mar 08").
        If conversion fails, returns the original value.
        """
        try:
            # Attempt to convert raw_date to a float.
            serial = float(raw_date)
            base_date = datetime(1899, 12, 30)  # Google Sheets base date.
            date_obj = base_date + timedelta(days=serial)
            return date_obj.strftime("%b %d")  # Example: "Mar 08"
        except Exception:
            # If it's not a serial number, return it as-is.
            return raw_date
    
    def isMoreThanOneWeekAgo(self, dateStr: str) -> bool:
        current_year = datetime.today().year
        today = datetime.today()
        date_obj = datetime.strptime(f"{dateStr} {current_year}", "%b %d %Y")
        one_week_ago = today - timedelta(days=8)
        if date_obj < one_week_ago:
            return True
        return False
    
job_posting_service = JobPostingService()
