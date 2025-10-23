# pages/pim_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from utils import config

class PIMPage:
    # Left sidebar PIM entry (robust)
    PIM_MENU = (
        By.XPATH,
        "//a[.//span[normalize-space()='PIM']]"
        " | //span[normalize-space()='PIM']/ancestor::a[1]"
        " | //span[normalize-space()='PIM']"
    )

    # Tabs inside PIM
    TAB_EMPLOYEE_LIST = (By.XPATH, "//a[normalize-space()='Employee List']")
    TAB_ADD_EMPLOYEE  = (By.XPATH, "//a[normalize-space()='Add Employee']")

    # Headers that prove we are on expected pages
    EMP_INFO_HEADER = (
        By.XPATH,
        "//h5[normalize-space()='Employee Information'] | //h6[normalize-space()='Employee Information']"
    )
    ADD_EMP_HEADER = (By.XPATH, "//h6[normalize-space()='Add Employee']")

    # Transient overlays
    LOADER = (By.CSS_SELECTOR, "div.oxd-form-loader")
    TOAST  = (By.CSS_SELECTOR, "div.oxd-toast")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, max(config.DEFAULT_WAIT, 15))

    # ---------- helpers ----------
    def _wait_overlay_gone(self):
        for loc in (self.LOADER, self.TOAST):
            try:
                self.wait.until(EC.invisibility_of_element_located(loc))
            except TimeoutException:
                pass

    def _safe_click(self, locator):
        self._wait_overlay_gone()
        el = self.wait.until(EC.presence_of_element_located(locator))
        try:
            self.wait.until(EC.element_to_be_clickable(locator)).click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", el)

    # ---------- actions ----------
    def go_to_pim(self) -> bool:
        """Click PIM in the left sidebar and wait until the PIM module is loaded."""
        self._safe_click(self.PIM_MENU)
        try:
            self.wait.until(
                EC.any_of(
                    EC.visibility_of_element_located(self.EMP_INFO_HEADER),
                    EC.presence_of_element_located(self.TAB_EMPLOYEE_LIST),
                    EC.presence_of_element_located(self.TAB_ADD_EMPLOYEE),
                )
            )
        except TimeoutException:
            return False
        return True

    def go_to_employee_list(self) -> bool:
        """Assumes we are in PIM; opens the Employee List tab and verifies header."""
        self._wait_overlay_gone()
        tab = self.wait.until(EC.presence_of_element_located(self.TAB_EMPLOYEE_LIST))
        try:
            self.wait.until(EC.element_to_be_clickable(self.TAB_EMPLOYEE_LIST)).click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", tab)

        self.wait.until(EC.visibility_of_element_located(self.EMP_INFO_HEADER))
        return True

    def open_employee_list(self) -> bool:
        """From anywhere: go to PIM then Employee List."""
        return self.go_to_pim() and self.go_to_employee_list()

    def open_add_employee(self) -> bool:
        """From anywhere: go to PIM then Add Employee; verify form header."""
        if not self.go_to_pim():
            return False
        self._wait_overlay_gone()
        tab = self.wait.until(EC.presence_of_element_located(self.TAB_ADD_EMPLOYEE))
        try:
            self.wait.until(EC.element_to_be_clickable(self.TAB_ADD_EMPLOYEE)).click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", tab)

        self.wait.until(EC.visibility_of_element_located(self.ADD_EMP_HEADER))
        return True
