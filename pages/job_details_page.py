# pages/job_details_page.py
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from utils import config


class JobDetailsPage:
    """
    Page object for the Job tab within an employee's record.
    Handles: Joined Date, Job Title, Job Category, Sub Unit, Location, Employment Status, Save.
    """

    # ---- Tabs / cards ----
    JOB_TAB = (By.XPATH, "//a[normalize-space()='Job']")

    JOB_CARD_HEADER = (
        By.XPATH,
        # Some OrangeHRM themes show "Job", others "Job Details" — support both.
        "//h6[normalize-space()='Job' or normalize-space()='Job Details']"
    )

    # ---- Fields ----
    JOINED_DATE_INPUT = (
        By.XPATH,
        "//label[normalize-space()='Joined Date']/..//following-sibling::div//input"
    )

    # Scoped Save to the Job card (avoid the other Save buttons on the page)
    JOB_SAVE_BTN = (
        By.XPATH,
        "("
        "//h6[normalize-space()='Job' or normalize-space()='Job Details']"
        "/ancestor::div[contains(@class,'orangehrm-card-container')]"
        "//button[@type='submit' and normalize-space()='Save']"
        ")[1]"
    )

    # ---- Global toasts/loaders (same behavior as other pages) ----
    SUCCESS_TOAST   = (By.XPATH, "//p[contains(@class,'oxd-text--toast-title') and contains(.,'Success')]")
    TOAST_CONTAINER = (By.XPATH, "//div[contains(@class,'oxd-toast')]")
    LOADER_OVERLAY  = (By.CSS_SELECTOR, "div.oxd-form-loader")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, max(config.DEFAULT_WAIT, 20))

    # ----------------- generic helpers -----------------
    def _wait_toast_gone(self):
        try:
            self.wait.until(EC.presence_of_element_located(self.TOAST_CONTAINER))
            self.wait.until(EC.invisibility_of_element_located(self.TOAST_CONTAINER))
        except TimeoutException:
            pass

    def _wait_loader_gone(self):
        try:
            self.wait.until(EC.invisibility_of_element_located(self.LOADER_OVERLAY))
        except TimeoutException:
            pass

    def _open_job_tab(self):
        self.wait.until(EC.element_to_be_clickable(self.JOB_TAB)).click()
        self._wait_loader_gone()
        # Ensure the Job card is visible
        self.wait.until(EC.visibility_of_element_located(self.JOB_CARD_HEADER))

    def _select_dropdown_by_label(self, label_text: str, option_text: str) -> str:
        """
        Open an OrangeHRM custom dropdown by its label and select option by visible text.
        If option_text == '*', it picks the first option available and returns the chosen text.
        Returns the text selected.
        """
        # Trigger element (the pretty select next to the label)
        dd = (
            By.XPATH,
            f"//label[normalize-space()='{label_text}']/..//following-sibling::div"
            f"//div[contains(@class,'oxd-select-text')]"
        )
        box = self.wait.until(EC.element_to_be_clickable(dd))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", box)
        try:
            box.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", box)

        # Option list
        if option_text == "*":
            # Choose the first actual option (skip placeholders)
            first_opt = (
                By.XPATH,
                "//div[@role='listbox']//span[normalize-space()!='' and not(contains(.,'-- Select --'))]"
            )
            el = self.wait.until(EC.element_to_be_clickable(first_opt))
            chosen = el.text.strip()
            el.click()
            self._wait_loader_gone()
            return chosen
        else:
            opt = (By.XPATH, f"//div[@role='listbox']//span[normalize-space()='{option_text}']")
            self.wait.until(EC.element_to_be_clickable(opt)).click()
            self._wait_loader_gone()
            return option_text

    def _robust_click_job_save(self):
        """Click the Save button inside the Job card with multiple fallbacks."""
        locator = self.JOB_SAVE_BTN
        btn = self.wait.until(EC.presence_of_element_located(locator))
        self._wait_loader_gone()
        self._wait_toast_gone()

        # Bring into safe view
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        self.driver.execute_script("window.scrollBy(0, 120);")

        # Try normal click → ActionChains → JS
        try:
            self.wait.until(EC.element_to_be_clickable(locator)).click()
            return
        except Exception:
            pass
        try:
            ActionChains(self.driver).move_to_element(btn).pause(0.1).click(btn).perform()
            return
        except Exception:
            pass
        self.driver.execute_script("arguments[0].click();", btn)

    # ----------------- main action -----------------
    def set_job_details(
        self,
        joined_date: str,
        job_title: str,
        job_category: str,
        sub_unit: str,
        location: str,
        employment_status: str,
    ) -> bool:
        """
        Fill the Job tab and save. Any dropdown param can be '*' to pick the first valid option.
        """
        # 1) Open Job tab
        self._open_job_tab()

        # 2) Joined Date
        date_el = self.wait.until(EC.visibility_of_element_located(self.JOINED_DATE_INPUT))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", date_el)
        date_el.clear()
        date_el.send_keys(joined_date)

        # 3) Dropdowns
        picked_title = self._select_dropdown_by_label("Job Title", job_title)
        picked_cat   = self._select_dropdown_by_label("Job Category", job_category)
        picked_unit  = self._select_dropdown_by_label("Sub Unit", sub_unit)
        picked_loc   = self._select_dropdown_by_label("Location", location)
        picked_stat  = self._select_dropdown_by_label("Employment Status", employment_status)

        # 4) Save
        self._robust_click_job_save()

        # 5) Verify success toast
        self.wait.until(EC.visibility_of_element_located(self.SUCCESS_TOAST))
        self._wait_toast_gone()
        self._wait_loader_gone()
        return True
