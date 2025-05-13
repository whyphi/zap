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
        self.driver = self._create_webdriver()
        self.gs = GoogleSheetsModule()
    
    def _create_webdriver(self, *chrome_args: str) -> webdriver.Chrome:
        """
        Configures and creates a headless Chrome webdriver with optional additional command-line options.

        Args:
            *chrome_args (str): Additional command-line arguments for ChromeOptions.
                If none are provided, the default options ["--headless", "--disable-gpu", "--no-sandbox"]
                will be used.

        Returns:
            webdriver.Chrome: A configured instance of the Chrome webdriver.
        """
        options = webdriver.ChromeOptions()
        # Use default options if no extra arguments are provided
        # "--headless":  Run Chrome in headless mode
        # "--disable-gpu":  Necessary for some environments
        # "--no-sandbox":  Good practice for running in Docker/Linux
        default_args = ["--headless", "--disable-gpu", "--no-sandbox"]
        args_to_use = chrome_args if chrome_args else default_args
        for arg in args_to_use:
            options.add_argument(arg)
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    def get_jobs(self, urlStr) -> List:
        """
        Fetches job postings from the given URL and returns a list of job details.

        This method navigates to the provided URL, locates the first table element on the page,
        and processes each row of the table body to extract job details such as the company name,
        job role, application link, and posting date. The extraction stops once a job posting date
        is determined to be more than one week old.
        
        **Due to this function's reliance on specific Github repo README formatting, this function
        will need to be updated/abstracted to handle changes to the repos in the future.

        Args:
            urlStr (str): The URL of the webpage containing job postings in a table format.

        Returns:
            List[dict]: A list of dictionaries, each containing keys 'company', 'role', 'link',
            and 'date' for the individual job postings.
        """
        self.driver.get(urlStr)
    
        table = self.driver.find_element(By.TAG_NAME, "table")
        body = table.find_element(By.TAG_NAME, "tbody")
        rows = body.find_elements(By.TAG_NAME, "tr")
                
        prevRowCompany = ""
        jobs = []
        for row in rows:
            cols = row.find_elements(By.XPATH, "td")
            date = cols[-1].text
            if (self.is_more_than_one_week_ago(date)):
                break
            
            company = ""
            role = ""
            link = ""
            
            try:
                company = cols[0].find_element(By.TAG_NAME, "strong").find_element(By.TAG_NAME, "a").text
                prevRowCompany = company
            except NoSuchElementException:
                try:
                    company = cols[0].text
                    if company == "↳":
                        company = prevRowCompany
                    else:
                        prevRowCompany = company
                except Exception:
                    company = "N/A"
                    
            
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
    
    def get_finance_jobs(self) -> List[Dict]:
        """
        Retrieves finance job opportunities from a specified Google Sheets document (currently RecruitU).

        This method utilizes the GoogleSheetsModule to fetch cell data from a predetermined Google Sheets
        document. It processes the data by separating header information from job rows, identifying the required
        columns (Company, Opportunity, Link, Deadline), and extracting relevant details. The method utilizes 
        the _convert_serial_to_date() helper function to convert serial date formats into a human-readable string format.

        Returns:
            List[dict]: A list of dictionaries, each containing job information with keys 'company', 'role',
            'link', and 'date'. Returns an empty list if no data is found or an error occurs.
        """
        JOBS_SHEET_ID = "15za1luZR08YmmBIFOAk6-GJB3T22StEuiZgFFuJeKW0"
        try:
            # Get sheet data with FORMULA render option to parse hyperlink formulas
            response = self.gs.get_all_cells(JOBS_SHEET_ID, "2027 Opportunities Tracker", "FORMULA")
            if not response.get("values"):
                return []
            
            # Get the same data with cell hyperlinks (for UI-inserted links)
            sheet_data = self.gs.get_sheet_with_grid_data(JOBS_SHEET_ID, "2027 Opportunities Tracker")
            
            # Define constants for row indices to improve readability and maintainability
            HEADER_ROW_INDEX = 5
            DATA_START_ROW_INDEX = 6
            DATA_END_ROW_INDEX = 31
            
            # Separate headers from rows
            headers = response["values"][HEADER_ROW_INDEX]
            rows = response["values"][DATA_START_ROW_INDEX:DATA_END_ROW_INDEX]
            
            # Find the column indices for the columns we want
            company_idx = headers.index("Company")
            opp_idx = headers.index("Opportunity")
            link_idx = headers.index("Link")
            
            deadline_idxs = [i for i, header in enumerate(headers) if header == "Deadline"]
            if len(deadline_idxs) > 1:
                deadline_idx = deadline_idxs[1]
            else:
                deadline_idx = deadline_idxs[0]
            
            # Loop through rows and extract only the columns we want
            job_listings = []
            hyperlink_regex = r'=HYPERLINK\("(.*?)","(.*?)"\)'
            for row_idx, row in enumerate(rows):
                if link_idx >= len(row):
                    continue
                raw_link = row[link_idx]
                # Try to extract hyperlink URL from formula first
                hyperlink_url = None
                match = re.match(hyperlink_regex, raw_link)
                if match:
                    hyperlink_url = match.group(1)
                else:
                    # If no formula hyperlink, try to get UI-inserted hyperlink from sheet_data
                    try:
                        # Row index is +6 because we started at row 6 in the response data
                        # Add 1 more because Google Sheets API is 0-indexed but our row_idx starts at 0
                        grid_row_idx = row_idx + DATA_START_ROW_INDEX + 1
                        hyperlink_url = self.gs.get_hyperlink_from_grid_data(sheet_data, grid_row_idx, link_idx)
                    except Exception as e:
                        print(f"Error getting UI hyperlink: {e}")
                
                # If no hyperlink found from either method, skip this row
                if not hyperlink_url:
                    continue
                
                raw_date = row[deadline_idx] if deadline_idx < len(row) else "N/A"
                date_str = self._convert_serial_to_date(raw_date)
                
                job = {
                    "company": row[company_idx] if company_idx < len(row) else "N/A",
                    "role": row[opp_idx] if opp_idx < len(row) else "N/A",
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

        Args:
            raw_date: The raw date value from Google Sheets (usually a serial number or string).

        Returns:
            str: A formatted date string or the original raw date if conversion is unsuccessful.
        """
        try:
            # Attempt to convert raw_date to a float
            serial = float(raw_date)
            base_date = datetime(1899, 12, 30)  # Google Sheets base date
            date_obj = base_date + timedelta(days=serial)
            return date_obj.strftime("%b %d")  # Example: "Mar 08"
        except Exception:
            # If it's not a serial number, return it as-is
            return raw_date
    
    def is_more_than_one_week_ago(self, dateStr: str) -> bool:
        """
        Determines if the given date string represents a date more than one week ago.

        Args:
            dateStr (str): A date string in the format "Mon DD" (e.g., "Mar 08").

        Returns:
            bool: True if the date is more than one week ago; False otherwise.
        """
        try:
            current_year = datetime.today().year
            today = datetime.today()
            date_obj = datetime.strptime(f"{dateStr} {current_year}", "%b %d %Y")
            one_week_ago = today - timedelta(days=8)
            if date_obj < one_week_ago:
                return True
            return False
        except ValueError as e:
            print(f"Error parsing date in standard format: {e}")
            # Hotfix: if dateStr is not in the format "Mon DD", but instead in the format 'DDd', i.e. "15d"
            # TODO: Keep an eye out for more edge cases and add them to the hotfix
            try:
                date_obj = dateStr[:-1]
                if int(date_obj) <= 7:
                    return True
                return False
            except (ValueError, IndexError) as e:
                print(f"Error parsing date in alternative format: {e}")
                return False
    
job_posting_service = JobPostingService()
