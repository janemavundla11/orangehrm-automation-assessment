# pages/employee_personal_page.py
import os
import time

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from utils import config


class EmployeePersonalPage:
    # ---------------- Personal Details (Employment Details) ----------------
    NATIONALITY_DD_ICON    = (By.XPATH, "//label[normalize-space()='Nationality']/..//following-sibling::div//i")
    MARITAL_STATUS_DD_ICON = (By.XPATH, "//label[normalize-space()='Marital Status']/..//following-sibling::div//i")
    DOB_INPUT              = (By.XPATH, "//label[normalize-space()='Date of Birth']/..//following-sibling::div//input")
    GENDER_FEMALE          = (By.XPATH, "//label[normalize-space()='Female']/span")
    GENDER_MALE            = (By.XPATH, "//label[normalize-space()='Male']/span")
    SAVE_BTN               = (By.XPATH, "//form//button[@type='submit' and normalize-space()='Save']")

    # Toasts / overlays
    SUCCESS_TOAST   = (By.XPATH, "//p[contains(@class,'oxd-text--toast-title') and contains(.,'Success')]")
    TOAST_CONTAINER = (By.XPATH, "//div[contains(@class,'oxd-toast')]")
    LOADER_OVERLAY  = (By.CSS_SELECTOR, "div.oxd-form-loader")

    # ---------------- Attachments card ----------------
    ATTACHMENTS_CARD_HDR = (By.XPATH, "//h6[normalize-space()='Attachments']")
    ATTACH_ADD_BTN = (
        By.XPATH,
        "//h6[normalize-space()='Attachments']/ancestor::div[contains(@class,'orangehrm-card-container')]"
        "//button[normalize-space()='Add']"
    )
    FILE_INPUT   = (By.CSS_SELECTOR, "input.oxd-file-input[type='file']")
    COMMENT_AREA = (By.CSS_SELECTOR, "textarea.oxd-textarea")

    # Scoped Save inside the Attachments card (the bottom Save)
    ATTACH_SAVE_BTN = (
        By.XPATH,
        "//h6[normalize-space()='Attachments']/ancestor::div[contains(@class,'orangehrm-card-container')]"
        "//button[@type='submit' and normalize-space()='Save']"
    )

    # Table container (for verifying the row appears)
    ATTACH_TABLE_CONTAINER = (
        By.XPATH,
        "//h6[normalize-space()='Attachments']/ancestor::div[contains(@class,'orangehrm-card-container')]"
        "//div[@class='oxd-table' or @role='table' or contains(@class,'oxd-table')]"
    )

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, max(config.DEFAULT_WAIT, 20))

    # ------------------ helpers ------------------
    def _get_attachments_card(self):
        """Find the Attachments card container element."""
        return self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//h6[normalize-space()='Attachments']/ancestor::div[contains(@class,'orangehrm-card-container')]"
        )))

    def _is_button_enabled(self, el) -> bool:
        """Check if a button element is truly enabled and clickable."""
        try:
            dis_attr = el.get_attribute("disabled")
            aria_dis = el.get_attribute("aria-disabled")
            cls = el.get_attribute("class") or ""
            pe = self.driver.execute_script("return getComputedStyle(arguments[0]).pointerEvents;", el)
            return (dis_attr is None) and (aria_dis not in ("true", "True")) and ("--disabled" not in cls) and (pe != "none")
        except Exception:
            return False

    def _wait_toast_gone(self):
        """Wait for any toast to appear (if it does) and then disappear."""
        try:
            self.wait.until(EC.presence_of_element_located(self.TOAST_CONTAINER))
            self.wait.until(EC.invisibility_of_element_located(self.TOAST_CONTAINER))
        except TimeoutException:
            pass

    def _wait_loader_gone(self):
        """Wait for form loader overlays to go away."""
        try:
            self.wait.until(EC.invisibility_of_element_located(self.LOADER_OVERLAY))
        except TimeoutException:
            pass

    def _open_dropdown(self, icon_locator):
        el = self.wait.until(EC.presence_of_element_located(icon_locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        self._wait_loader_gone()
        try:
            self.wait.until(EC.element_to_be_clickable(icon_locator)).click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", el)

    def _select_from_custom_dropdown(self, icon_locator, visible_text):
        self._open_dropdown(icon_locator)
        option = (By.XPATH, f"//div[@role='listbox']//span[normalize-space()='{visible_text}']")
        self.wait.until(EC.element_to_be_clickable(option)).click()
        self._wait_loader_gone()

    def _scroll_into_view_everywhere(self, el):
        """
        Scroll the element into view in BOTH the window and any scrollable ancestor.
        Also nudges a bit to avoid sticky footers.
        """
        self.driver.execute_script("""
            const el = arguments[0];

            // First, native center into view in the window
            el.scrollIntoView({block: 'center'});

            // Then, find nearest scrollable ancestor and center inside it
            function isScrollable(n) {
              if (!n) return false;
              const cs = getComputedStyle(n);
              const oy = cs.overflowY;
              return (oy === 'auto' || oy === 'scroll') && n.scrollHeight > n.clientHeight;
            }
            let node = el.parentElement;
            while (node && !isScrollable(node)) node = node.parentElement;
            if (node) {
              const rEl = el.getBoundingClientRect();
              const rHost = node.getBoundingClientRect();
              const delta = (rEl.top - rHost.top) - (rHost.height/2 - rEl.height/2);
              node.scrollTop += delta;
            }
        """, el)
        # Also push the window a bit in case a sticky footer overlaps
        self.driver.execute_script("window.scrollBy(0, 180);")

    def _click_attachments_save(self) -> None:
        """Click the Save button inside the Attachments card with multiple fallbacks."""
        card = self._get_attachments_card()

        def _refind_btn():
            return card.find_element(By.XPATH, ".//button[normalize-space()='Save']")

        def _center_is_button(btn):
            # Return True if the element under the center point is the button (or inside it)
            return self.driver.execute_script("""
                const el = arguments[0];
                const r = el.getBoundingClientRect();
                const x = Math.floor(r.left + r.width/2);
                const y = Math.floor(r.top + r.height/2);
                const t = document.elementFromPoint(x, y);
                return t && (t === el || el.contains(t));
            """, btn)

        self._wait_loader_gone()
        self._wait_toast_gone()

        # Wait until truly enabled
        WebDriverWait(self.driver, 10).until(lambda d: self._is_button_enabled(_refind_btn()))

        attempts = []

        # Always re-find + re-scroll just before each attempt (framework may re-render)
        try:
            btn = _refind_btn()
            self._scroll_into_view_everywhere(btn)
            self.wait.until(EC.element_to_be_clickable((
                By.XPATH,
                "//h6[normalize-space()='Attachments']/ancestor::div[contains(@class,'orangehrm-card-container')]//button[normalize-space()='Save']"
            ))).click()
            return
        except Exception as e:
            attempts.append(f"std click: {e}")

        try:
            btn = _refind_btn()
            self._scroll_into_view_everywhere(btn)
            ActionChains(self.driver).move_to_element(btn).pause(0.05).click(btn).perform()
            return
        except Exception as e:
            attempts.append(f"actions click: {e}")

        try:
            btn = _refind_btn()
            self._scroll_into_view_everywhere(btn)
            # Dispatch real mouse events to satisfy frameworks that listen for them
            self.driver.execute_script("""
                const el = arguments[0];
                for (const type of ['pointerdown','mousedown','mouseup','click']) {
                    el.dispatchEvent(new MouseEvent(type, {bubbles:true, cancelable:true, view:window}));
                }
            """, btn)
            return
        except Exception as e:
            attempts.append(f"js mouse events: {e}")

        try:
            btn = _refind_btn()
            self._scroll_into_view_everywhere(btn)
            self.driver.execute_script("arguments[0].focus();", btn)
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            return
        except Exception as e:
            attempts.append(f"enter key: {e}")

        try:
            btn = _refind_btn()
            self._scroll_into_view_everywhere(btn)
            self.driver.execute_script("arguments[0].focus();", btn)
            ActionChains(self.driver).send_keys(" ").perform()  # SPACE activates buttons in many UIs
            return
        except Exception as e:
            attempts.append(f"space key: {e}")

        try:
            btn = _refind_btn()
            self._scroll_into_view_everywhere(btn)
            # If something overlaps, click the element under the center point
            if not _center_is_button(btn):
                self.driver.execute_script("window.scrollBy(0, -60);")  # micro-adjust and try again
            clicked = self.driver.execute_script("""
                const el = arguments[0];
                const r = el.getBoundingClientRect();
                const x = Math.floor(r.left + r.width/2);
                const y = Math.floor(r.top + r.height/2);
                const t = document.elementFromPoint(x, y);
                if (t) { t.click(); return true; }
                return false;
            """, btn)
            if clicked:
                return
        except Exception as e:
            attempts.append(f"elementFromPoint click: {e}")

        try:
            # Fallback: submit the enclosing form (works even if a cover steals the click)
            btn = _refind_btn()
            self.driver.execute_script("""
                const btn = arguments[0];
                const form = btn.closest('form');
                if (form) {
                    const ev = new Event('submit', {bubbles:true, cancelable:true});
                    form.dispatchEvent(ev);
                    if (typeof form.submit === 'function') form.submit();
                } else {
                    btn.click();
                }
            """, btn)
            return
        except Exception as e:
            attempts.append(f"form submit: {e}")

        raise AssertionError("Attachments → Save could not be activated. Attempts: " + " | ".join(attempts))

    # ------------------ actions ------------------
    def set_personal_details(self, nationality: str, marital_status: str, dob: str, gender: str) -> bool:
        """Fill Employment/Personal details and save."""
        self._select_from_custom_dropdown(self.NATIONALITY_DD_ICON, nationality)
        self._select_from_custom_dropdown(self.MARITAL_STATUS_DD_ICON, marital_status)

        self.wait.until(EC.visibility_of_element_located(self.DOB_INPUT)).clear()
        self.driver.find_element(*self.DOB_INPUT).send_keys(dob)

        if gender.lower().startswith("f"):
            self.wait.until(EC.element_to_be_clickable(self.GENDER_FEMALE)).click()
        else:
            self.wait.until(EC.element_to_be_clickable(self.GENDER_MALE)).click()

        self._wait_loader_gone()
        self.driver.find_element(*self.SAVE_BTN).click()

        self.wait.until(EC.visibility_of_element_located(self.SUCCESS_TOAST))
        self._wait_toast_gone()
        self._wait_loader_gone()
        return True

    def add_attachment(self, file_path: str, comment: str = "") -> bool:
        """
        Attach a file in the Attachments card, EXPLICITLY scroll back down, click Save,
        and verify it appears in the table.
        """
        file_name = os.path.basename(file_path)

        # Make sure the card header is in view first
        self._wait_toast_gone()
        hdr = self.wait.until(EC.visibility_of_element_located(self.ATTACHMENTS_CARD_HDR))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", hdr)

        # Click "Add"
        add_btn = self.wait.until(EC.element_to_be_clickable(self.ATTACH_ADD_BTN))
        try:
            add_btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", add_btn)

        # Upload the file
        file_input = self.wait.until(EC.presence_of_element_located(self.FILE_INPUT))
        self.wait.until(lambda d: file_input.is_enabled())
        file_input.send_keys(file_path)

        # Ensure browser registered the file (prevents racing)
        self.wait.until(lambda d: d.execute_script(
            "return arguments[0].files && arguments[0].files.length > 0;", file_input
        ))

        # Optional comment
        if comment:
            self.driver.find_element(*self.COMMENT_AREA).send_keys(comment)

        # --------- CRITICAL: Scroll AFTER attaching, BEFORE clicking Save ---------
        # Some OrangeHRM builds reflow the page after file selection; force a hard scroll.
        self.driver.execute_script("window.scrollTo({top: document.body.scrollHeight, behavior: 'instant'});")

        # Bring the specific Save (inside the Attachments card) into centered view, then nudge
        card = self._get_attachments_card()
        save_btn = card.find_element(By.XPATH, ".//button[normalize-space()='Save']")
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", save_btn)
        self.driver.execute_script("window.scrollBy(0, 160);")  # nudge past sticky footer/bars

        # Wait until the Save is truly enabled (handles aria-disabled / pointer-events)
        WebDriverWait(self.driver, 10).until(lambda d: self._is_button_enabled(save_btn))

        # Click Save (robust helper still handles overlays & re-render edge cases)
        self._click_attachments_save()

        # Verify toast and row in table
        self.wait.until(EC.visibility_of_element_located(self.SUCCESS_TOAST))
        self._wait_toast_gone()

        filename_cell = (
            By.XPATH,
            "//h6[normalize-space()='Attachments']/ancestor::div[contains(@class,'orangehrm-card-container')]"
            "//div[@role='table' or contains(@class,'oxd-table')]//div[contains(normalize-space(), %s)]"
        )
        self.wait.until(EC.visibility_of_element_located((filename_cell[0], filename_cell[1] % f"'{file_name}'")))
        return True
