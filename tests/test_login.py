# tests/test_login.py
import logging, random
from utils import config
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.pim_page import PIMPage
from pages.add_employee_page import AddEmployeePage
from pages.employee_personal_page import EmployeePersonalPage
import pytest
# from pages.employee_job_page import EmployeeJobPage
from pages.job_details_page import JobDetailsPage
from pages.employee_list_page import EmployeeListPage


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def test_can_login(driver):
    logger.info("Navigating to login page")
    driver.get(config.BASE_URL)

    logger.info(f"Logging in with {config.USERNAME}/{config.PASSWORD}")
    WebDriverWait(driver, config.DEFAULT_WAIT).until(
        EC.visibility_of_element_located((By.NAME, "username"))
    ).send_keys(config.USERNAME)
    driver.find_element(By.NAME, "password").send_keys(config.PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    logger.info("Waiting for the Dashboard to appear")
    WebDriverWait(driver, config.DEFAULT_WAIT).until(
        EC.visibility_of_element_located((By.XPATH, "//h6[normalize-space()='Dashboard']"))
    )
    logger.info("✅ Login successful — Dashboard page visible")


def login_quick(driver):
    driver.get(config.BASE_URL)
    WebDriverWait(driver, config.DEFAULT_WAIT).until(
        EC.visibility_of_element_located((By.NAME, "username"))
    ).send_keys(config.USERNAME)
    driver.find_element(By.NAME, "password").send_keys(config.PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    WebDriverWait(driver, config.DEFAULT_WAIT).until(
        EC.visibility_of_element_located((By.XPATH, "//h6[normalize-space()='Dashboard']"))
    )

def test_can_navigate_to_pim(driver):
    logger.info("Step 1–3: Logging in and landing on Dashboard")
    login_quick(driver)

    logger.info("Step 4: Clicking PIM in the side menu")
    pim = PIMPage(driver)
    assert pim.go_to_pim()
    logger.info("✅ Navigated to the PIM page (Employee Information visible)")

def test_can_add_employee(driver):
    logger.info("Login and navigate to Add Employee page")
    login_quick(driver)

    pim = PIMPage(driver)
    assert pim.go_to_pim()
    assert pim.open_add_employee()

    add = AddEmployeePage(driver)
    assert add.is_loaded()

    first  = f"Jane{random.randint(100,999)}"
    middle = "QA"
    last   = "Tester"

    logger.info(f"Filling employee details: {first} {middle} {last}")
    add.fill_employee_details(first, middle, last)

    logger.info("Saving new employee record")
    assert add.save_employee()
    logger.info("✅ Employee successfully saved")


def test_set_personal_details_and_attachments(driver, tmp_path):
    logger.info("Login → PIM → Add Employee")
    login_quick(driver)
    pim = PIMPage(driver)
    assert pim.go_to_pim()
    assert pim.open_add_employee()

    add = AddEmployeePage(driver)
    assert add.is_loaded()

    # Step 6: create the employee
    first  = f"Jane{random.randint(1000,9999)}"
    middle = "QA"
    last   = "Tester"
    logger.info(f"Filling employee details: {first} {middle} {last}")
    add.fill_employee_details(first, middle, last)
    logger.info("Saving new employee record")
    assert add.save_employee()
    logger.info("✅ Employee saved; now on Personal Details screen")

    # Step 7: Employment/Personal details
    personal = EmployeePersonalPage(driver)
    logger.info("Setting Personal Details: Nationality=South African, Marital=Single, DOB=1995-05-05, Gender=Female")
    assert personal.set_personal_details(
        nationality="South African",
        marital_status="Single",
        dob="1995-05-05",
        gender="Female"
    )
    logger.info("✅ Personal details saved (success toast shown)")

    # Step 8: Attachments
    dummy = tmp_path / "attachment.txt"
    dummy.write_text("Demo file for OrangeHRM attachment test (no real info).")
    logger.info(f"Uploading attachment: {dummy}")
    assert personal.add_attachment(str(dummy))
    logger.info("✅ Attachment uploaded and listed in the table")


def test_set_job_details(driver):
    """
    Step 9: Job tab — fill and save job details, verify success.
    """
    logger.info("Login → PIM → Add Employee → Save → Job tab")
    login_quick(driver)

    pim = PIMPage(driver)
    assert pim.go_to_pim()
    assert pim.open_add_employee()

    add = AddEmployeePage(driver)
    assert add.is_loaded()

    # Create an employee quickly
    first = f"Jane{random.randint(1000,9999)}"
    middle = "QA"
    last = "Tester"
    logger.info(f"Creating employee for job details: {first} {middle} {last}")
    add.fill_employee_details(first, middle, last)
    assert add.save_employee()
    logger.info("Employee saved; now setting Job details")

    job = JobDetailsPage(driver)
    assert job.set_job_details(
        joined_date="2025-01-11",
        job_title="QA Engineer",
        job_category="Professionals",
        sub_unit="Quality Assurance",
        location="*",                 # use '*' to pick the first available, or put an exact visible option
        employment_status="Full-Time Contract",  # match exact visible text in your instance
    )
    logger.info("✅ Job details saved (success toast shown)")

    def test_open_employee_list(driver):
        """Step 10: Click Employee List and verify Employee Information page."""
        logger.info("Navigating to Employee List")
        login_quick(driver)  # this is the helper you already have
        pim = PIMPage(driver)
        assert pim.go_to_pim()
        emp_list = EmployeeListPage(driver)
        assert emp_list.open_employee_list()
        logger.info("✅ Employee Information page displayed")




