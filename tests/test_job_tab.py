# tests/test_job_tab.py
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.pim_page import PIMPage
from pages.employee_list_page import EmployeeListPage
from utils import config

logger = logging.getLogger(__name__)

def _quick_login(driver):
    driver.get(config.BASE_URL)
    WebDriverWait(driver, config.DEFAULT_WAIT).until(
        EC.visibility_of_element_located((By.NAME, "username"))
    ).send_keys(config.USERNAME)
    driver.find_element(By.NAME, "password").send_keys(config.PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    WebDriverWait(driver, config.DEFAULT_WAIT).until(
        EC.visibility_of_element_located((By.XPATH, "//h6[normalize-space()='Dashboard']"))
    )

def test_open_employee_list(driver):
    """Step 10: Click Employee List and verify Employee Information page."""
    logger.info("Navigating to Employee List")
    _quick_login(driver)

    pim = PIMPage(driver)
    assert pim.go_to_pim()

    emp_list = EmployeeListPage(driver)
    assert emp_list.open_employee_list()
    logger.info("✅ Employee Information page displayed")
