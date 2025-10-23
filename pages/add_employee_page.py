# pages/add_employee_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import config

class AddEmployeePage:
    # --- Locators on the Add Employee form ---
    HEADER       = (By.XPATH, "//h6[normalize-space()='Add Employee']")
    FIRST_NAME   = (By.NAME, "firstName")
    MIDDLE_NAME  = (By.NAME, "middleName")
    LAST_NAME    = (By.NAME, "lastName")
    SAVE_BTN     = (By.XPATH, "//button[@type='submit']")

    # Success toast shown after save
    SUCCESS_TOAST = (
        By.XPATH,
        "//p[contains(@class,'oxd-text--toast-title') and contains(.,'Success')]"
    )

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, config.DEFAULT_WAIT)

    # --- Assertions / waits ---
    def is_loaded(self) -> bool:
        """Confirm the Add Employee page is visible."""
        self.wait.until(EC.visibility_of_element_located(self.HEADER))
        self.wait.until(EC.visibility_of_element_located(self.FIRST_NAME))
        return True

    # --- Actions ---
    def fill_employee_details(self, first: str, middle: str, last: str) -> None:
        """Type the employee's first, middle, and last names."""
        self.wait.until(EC.visibility_of_element_located(self.FIRST_NAME)).clear()
        self.driver.find_element(*self.FIRST_NAME).send_keys(first)

        self.driver.find_element(*self.MIDDLE_NAME).clear()
        self.driver.find_element(*self.MIDDLE_NAME).send_keys(middle)

        self.driver.find_element(*self.LAST_NAME).clear()
        self.driver.find_element(*self.LAST_NAME).send_keys(last)

    def save_employee(self) -> bool:
        """Click Save and wait for the success toast."""
        self.driver.find_element(*self.SAVE_BTN).click()
        self.wait.until(EC.visibility_of_element_located(self.SUCCESS_TOAST))
        return True
