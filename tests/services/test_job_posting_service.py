import pytest
from datetime import datetime, timedelta
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from chalicelib.services.JobPostingService import job_posting_service


# Dummy classes to simulate Selenium elements

class DummyElement:
    """A basic dummy element with text and attributes"""
    def __init__(self, text="", attributes=None):
        self.text = text
        self.attributes = attributes or {}

    def find_element(self, by, value):
        # By default we simulate nothing found
        raise NoSuchElementException(f"DummyElement: No element for {value}")

    def get_attribute(self, attr):
        return self.attributes.get(attr, "")


class DummyElementWrapper:
    """
    Wraps an element (e.g. the result of a <strong> lookup) so that calling
    find_element("a") returns an element with the provided text and href
    """
    def __init__(self, text, href):
        self.text = text
        self.href = href

    def find_element(self, by, value):
        if by == By.TAG_NAME and value == "a":
            return DummyElement(text=self.text, attributes={"href": self.href})
        raise NoSuchElementException()


class DummyCol:
    """
    Simulates a table cell
    For nested lookups (e.g. extracting <strong><a>...</a></strong>),
    set strong_a_text and strong_a_href
    If raise_strong is True (or strong_a_text is None), a lookup for a <strong>
    will raise NoSuchElementException
    """
    def __init__(self, text="", strong_a_text=None, strong_a_href=None, raise_strong=False):
        self.text = text
        self.strong_a_text = strong_a_text
        self.strong_a_href = strong_a_href
        self.raise_strong = raise_strong

    def find_element(self, by, value):
        if by == By.TAG_NAME and value == "strong":
            if self.raise_strong or self.strong_a_text is None:
                raise NoSuchElementException("No <strong> element found")
            # Return dummy wrapper that when asked for <a> returns the link element
            return DummyElementWrapper(self.strong_a_text, self.strong_a_href)
        elif by == By.TAG_NAME and value == "a":
            # For cases where a direct lookup for <a> is needed
            return DummyElement(text=self.text, attributes={"href": self.strong_a_href})
        raise NoSuchElementException()


class DummyRow:
    """
    Simulates a table row
    The method find_elements(By.XPATH, "td") returns the list of dummy columns
    """
    def __init__(self, cols):
        self.cols = cols

    def find_elements(self, by, value):
        if by == By.XPATH and value == "td":
            return self.cols
        return []


class DummyTbody:
    """
    Simulates a <tbody> element
    """
    def __init__(self, rows):
        self.rows = rows

    def find_elements(self, by, value):
        if by == By.TAG_NAME and value == "tr":
            return self.rows
        return []


class DummyTable:
    """
    Simulates a <table> element
    """
    def __init__(self, tbody):
        self._tbody = tbody

    def find_element(self, by, value):
        if by == By.TAG_NAME and value == "tbody":
            return self._tbody
        raise NoSuchElementException()


class DummyDriver:
    """
    Simulates the Selenium WebDriver
    Records the URL passed to .get() and returns the dummy table when find_element is called
    """
    def __init__(self, table):
        self._table = table
        self.called_url = None

    def get(self, url):
        self.called_url = url

    def find_element(self, by, value):
        if by == By.TAG_NAME and value == "table":
            return self._table
        raise NoSuchElementException()


# Service with a dummy driver

@pytest.fixture
def job_service():
    """
    Creates a JobPostingService instance and overrides its driver with a dummy
    driver that returns a dummy table structure.
    """    
    today = datetime.today()
    date_within = today.strftime("%b %d")
    date_old = (today - timedelta(days=9)).strftime("%b %d")
    
    # Row 1: Has complete data in columns
    #   - Column 0: Company info is present
    #   - Column 1: Role info with nested <strong><a> exists
    #   - Column 3: Contains a link (won't be used because role branch succeeded)
    #   - Last column: Date within one week
    row1 = DummyRow([
        DummyCol(strong_a_text="CompanyX", strong_a_href="http://companyX.com"),  # col0: company info
        DummyCol(strong_a_text="Engineer", strong_a_href="http://job1.com"),         # col1: role info
        DummyCol(text="Extra"),                                                     # col2: extra column (unused)
        DummyCol(text="ignored", strong_a_href="http://job1-alt.com"),                # col3: link fallback
        DummyCol(text=date_within)                                                  # col4: date column
    ])
    
    # Row 2: Missing nested data in col0 and col1
    #   - Column 0: Raises exception => should use previous row's company ("CompanyX")
    #   - Column 1: Raises exception => role falls back to plain text ("Developer")
    #   - Column 3: Provides link via <a> lookup
    #   - Last column: Date within one week
    row2 = DummyRow([
        DummyCol(text="ignored", raise_strong=True),              # col0: missing company info
        DummyCol(text="Developer", raise_strong=True),            # col1: missing role nested data; fallback to text "Developer"
        DummyCol(text="Extra"),                                   # col2: extra
        DummyCol(text="ignored", strong_a_href="http://job2.com"),  # col3: link fallback used since role branch didn't set link
        DummyCol(text=date_within)                                # col4: date column
    ])
    
    # Row 3: Has a date older than one week, row should not be processed
    row3 = DummyRow([
        DummyCol(strong_a_text="CompanyY", strong_a_href="http://companyY.com"),  # col0
        DummyCol(strong_a_text="Manager", strong_a_href="http://job3.com"),         # col1
        DummyCol(text="Extra"),                                                     # col2
        DummyCol(text="ignored", strong_a_href="http://job3-alt.com"),              # col3
        DummyCol(text=date_old)                                                     # col4: date older than one week
    ])
    
    dummy_tbody = DummyTbody(rows=[row1, row2, row3])
    dummy_table = DummyTable(tbody=dummy_tbody)
    
    dummy_driver = DummyDriver(table=dummy_table)
    job_posting_service.driver = dummy_driver

    return job_posting_service


def test_get_jobs(job_service):
    """
    Tests the getJobs() method:
      - Verifies that the driver navigates to the provided URL.
      - Processes rows until a row with a date older than one week is encountered.
      - Uses nested element lookups where available and falls back to previous row's company or plain text.
    """
    test_url = "http://example.com/jobs"
    jobs = job_service.getJobs(test_url)

    assert job_service.driver.called_url == test_url

    # The third row should cause the loop to break, only row1 and row2 are processed
    assert len(jobs) == 2

    # Row 1: complete data from nested lookups
    expected_job1 = {
        "company": "CompanyX",
        "role": "Engineer",
        "link": "http://job1.com",  # taken from col1 nested link
        "date": job_service.driver._table._tbody.rows[0].cols[-1].text  # date_within
    }
    # Row 2: company missing (fallback to previous "CompanyX"), role falls back to plain text, and link from col3
    expected_job2 = {
        "company": "CompanyX",  # fallback from row1's company
        "role": "Developer",
        "link": "http://job2.com",  # from col3 lookup
        "date": job_service.driver._table._tbody.rows[1].cols[-1].text  # date_within
    }

    assert jobs[0] == expected_job1
    assert jobs[1] == expected_job2

def test_get_finance_jobs(job_service):
    """
    Verifies that getFinanceJobs correctly processes a dummy Google Sheets response.
    The response is simulated to include a header row at index 5 and two data rows.
    """
    # Create a dummy response similar to what GoogleSheetsModule would return
    # Note: The service expects the headers at index 5 and rows 6:31 as data
    dummy_response = {
        "values": [
            [], [], [], [], [],
            ["Company", "Opportunity", "Link", "Deadline"],
            ["CompanyA", "Engineer", '=HYPERLINK("http://jobA.com","Job A")', "44197"],
            ["CompanyB", "Manager", '=HYPERLINK("http://jobB.com","Job B")', "Not a serial"]
        ]
    }

    # Replace Google Sheets module with one that returns dummy response
    class DummyGS:
        def get_all_cells(self, sheet_id, sheet_name, mode):
            return dummy_response

    job_service.gs = DummyGS()

    jobs = job_service.getFinanceJobs()

    assert len(jobs) == 2

    # For first row, serial "44197" should convert to date
    # (44197 corresponds to 2021-01-01 when using base date 1899-12-30.)
    assert jobs[0]["company"] == "CompanyA"
    assert jobs[0]["role"] == "Engineer"
    assert jobs[0]["link"] == "http://jobA.com"
    assert jobs[0]["date"] == "Jan 01"

    # For second row, conversion should fail and return original string
    assert jobs[1]["company"] == "CompanyB"
    assert jobs[1]["role"] == "Manager"
    assert jobs[1]["link"] == "http://jobB.com"
    assert jobs[1]["date"] == "Not a serial"


def test_get_finance_jobs_empty(job_service):
    """
    Verifies that if the Google Sheets response does not contain 'values', getFinanceJobs returns an empty list.
    """
    dummy_response = {}  # No "values" key
    class DummyGS:
        def get_all_cells(self, sheet_id, sheet_name, mode):
            return dummy_response
    job_service.gs = DummyGS()

    jobs = job_service.getFinanceJobs()
    assert jobs == []


def test_get_finance_jobs_exception(job_service, capsys):
    """
    Verifies that if an exception is raised while fetching data from Google Sheets,
    getFinanceJobs returns an empty list.
    """
    class DummyGS:
        def get_all_cells(self, sheet_id, sheet_name, mode):
            raise Exception("Test Exception")
    job_service.gs = DummyGS()

    jobs = job_service.getFinanceJobs()
    # Exception should be caught and method should return empty list
    assert jobs == []


def test_convert_serial_to_date(job_service):
    """
    Tests _convert_serial_to_date with a valid serial and with invalid data.
    """
    result = job_service._convert_serial_to_date("44197")
    assert result == "Jan 01"

    result = job_service._convert_serial_to_date("invalid")
    assert result == "invalid"


def test_is_more_than_one_week_ago(job_service):
    """
    Tests isMoreThanOneWeekAgo with dates within and beyond one week.
    """
    today = datetime.today()
    date_within = (today - timedelta(days=5)).strftime("%b %d")
    date_old = (today - timedelta(days=9)).strftime("%b %d")

    assert job_service.isMoreThanOneWeekAgo(date_within) is False
    assert job_service.isMoreThanOneWeekAgo(date_old) is True