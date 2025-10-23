# pages/employee_list_page.py
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from utils import config
from pages.pim_page import PIMPage


class EmployeeListPage:
    EMP_INFO_HEADER = (
        By.XPATH,
        "//h5[normalize-space()='Employee Information'] | //h6[normalize-space()='Employee Information']"
    )

    # Search controls
    NAME_INPUT = (By.XPATH, "//label[normalize-space()='Employee Name']/..//input")
    ID_INPUT   = (By.XPATH, "//label[normalize-space()='Employee Id']/..//input")
    SEARCH_BTN = (By.XPATH, "//button[@type='submit' and normalize-space()='Search']")

    # Results table
    TABLE_ROWS = (By.XPATH, "//div[@role='table']//div[@role='row' and position()>1]")
    TABLE_TEXT = (By.XPATH, "//div[@role='table']")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, max(config.DEFAULT_WAIT, 15))

    def is_loaded(self) -> bool:
        try:
            self.wait.until(EC.visibility_of_element_located(self.EMP_INFO_HEADER))
            return True
        except TimeoutException:
            return False

    def open_employee_list(self) -> bool:
        """Click PIM → Employee List and verify page is loaded."""
        pim = PIMPage(self.driver)
        return pim.open_employee_list()

    def search_employee(self, name: str | None = None, emp_id: str | None = None) -> bool:
        """Fill the search form (name and/or id) and click Search (handles autocomplete)."""
        self.wait.until(EC.visibility_of_element_located(self.TABLE_TEXT))  # ensure page loaded

        if name:
            # Find Employee Name field (autocomplete input)
            name_input = self.wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//label[normalize-space()='Employee Name']/..//following-sibling::div//input")
                )
            )

            # Clear it and type the name
            name_input.click()
            name_input.send_keys(Keys.CONTROL, 'a')
            name_input.send_keys(Keys.DELETE)
            name_input.send_keys(name)

            # Wait for dropdown suggestions and pick the first one (or the one that matches)
            try:
                dropdown_item = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, f"//div[contains(@class,'oxd-autocomplete-dropdown')]//span[contains(., '{name}')]")
                    )
                )
                dropdown_item.click()
            except TimeoutException:
                # Fallback — press Enter if dropdown didn’t appear
                name_input.send_keys(Keys.ENTER)

        if emp_id:
            emp_input = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH,
                     "//label[contains(.,'Employee Id') or contains(.,'Employee ID')]/..//following-sibling::div//input")
                )
            )
            emp_input.clear()
            emp_input.send_keys(emp_id)

        # Click Search
        search_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and normalize-space()='Search']"))
        )
        try:
            search_btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", search_btn)

        # Wait for table to refresh (there’s usually a short loader)
        self.wait.until(EC.presence_of_element_located(self.TABLE_TEXT))
        time.sleep(1)  # small buffer for OrangeHRM animation

        try:
            before = self.driver.find_element(*self.TABLE_TEXT).text
        except Exception:
            before = ""

            # click Search (your existing robust click)
        btn = self.wait.until(EC.element_to_be_clickable(self.SEARCH_BTN))
        try:
            btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)

        # wait for table to change (or at least ensure presence)
        self.wait.until(EC.presence_of_element_located(self.TABLE_TEXT))
        WebDriverWait(self.driver, 8).until(
            lambda d: d.find_element(*self.TABLE_TEXT).text != before
        )
        return True


    # pages/employee_list_page.py  (inside EmployeeListPage)

    def verify_result_contains(self, text: str, timeout: int = 12) -> bool:
        """
        Wait until any cell in the results table contains `text` (case-insensitive).
        More reliable than reading the whole table's .text once.
        """
        locator = (
            By.XPATH,
            "//div[@role='table' or contains(@class,'oxd-table')]"
            "//div[@role='rowgroup']//div[@role='row']"
            "//div[@role='cell'][contains(translate(normalize-space(.),"
            " 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),"
            f" '{text.strip().lower()}')]"
        )

        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            # Optional: dump current first row text to help debug
            try:
                first_row = self.driver.find_element(
                    By.XPATH,
                    "//div[@role='table' or contains(@class,'oxd-table')]"
                    "//div[@role='rowgroup']//div[@role='row']"
                ).text
                raise AssertionError(f"Could not find '{text}' in results. First row: {first_row}")
            except Exception:
                return False


