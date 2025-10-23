# tests/test_employee_search.py
import logging, random, string
import os

import pytest
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.pim_page import PIMPage
from pages.employee_list_page import EmployeeListPage
from pages.add_employee_page import AddEmployeePage as EmployeeAddPage, AddEmployeePage
from utils import config
from datetime import datetime

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


@pytest.mark.order(11)
def test_search_newly_added_employee(driver):
    """
    Step 11:
      - Create a unique employee.
      - Navigate to Employee List.
      - Search by the employee's name.
      - Verify the record appears in the results table.
    """
    _quick_login(driver)

    # Unique name
    first = f"Jane{''.join(random.choices(string.digits, k=4))}"
    middle = "QA"
    last = "Tester"

    # --- Add the employee ---
    pim = PIMPage(driver)
    assert pim.open_add_employee(), "Could not open Add Employee page"

    add_page = AddEmployeePage(driver)
    assert add_page.is_loaded(), "Add Employee page not loaded"
    add_page.fill_employee_details(first, middle, last)
    assert add_page.save_employee(), "Saving the new employee did not show success toast"
    logger.info(f"✅ Employee {first} {last} added")

    # After save, OrangeHRM usually lands on Personal Details. Go back to Employee List.
    assert pim.go_to_employee_list(), "Could not navigate to Employee List"

    # --- Search for the newly added employee ---
    emp_list = EmployeeListPage(driver)
    expected_first_middle = f"{first} {middle}"  # e.g., "Jane6580 QA"

    assert emp_list.search_employee(name=first)
    assert emp_list.verify_result_contains(expected_first_middle)
    # you can also assert last name if you like:
    assert emp_list.verify_result_contains(last)

    logger.info(f"✅ Found {first} in the Employee List results")

    # --- Take screenshot after verification ---
    os.makedirs("screenshots", exist_ok=True)  # ensures folder exists
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = f"screenshots/employee_search_{timestamp}.png"
    driver.save_screenshot(screenshot_path)
    logger.info(f"📸 Screenshot saved to {screenshot_path}")