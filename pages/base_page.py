"""BasePage — the shared toolkit every page object inherits.

Design intent:
- A page object owns *locators* and *intent* ("login as X"), never raw
  WebDriver synchronisation boilerplate.
- Every interaction goes through an explicit wait. There is no time.sleep()
  and no implicit wait anywhere in this framework.
- click() falls back to a JS click when a real click is intercepted (common on
  ad-heavy pages where an overlay briefly covers the target).

A "locator" is a (By, value) tuple, e.g. (By.ID, "search_product").
"""
from __future__ import annotations

from typing import Optional, Tuple

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    TimeoutException,
)
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from config.config import Config
from utils.logger import get_logger

Locator = Tuple[str, str]


class BasePage:
    def __init__(self, driver: WebDriver, timeout: Optional[int] = None):
        self.driver = driver
        self.timeout = timeout or Config.EXPLICIT_TIMEOUT
        self.log = get_logger(self.__class__.__name__)

    # --- navigation -------------------------------------------------------
    def open(self, path: str = "") -> "BasePage":
        url = Config.BASE_URL.rstrip("/") + "/" + path.lstrip("/") if path else Config.BASE_URL
        self.log.info("Navigating to %s", url)
        self.driver.get(url)
        self._wait_for_cloudflare()
        return self

    def _wait_for_cloudflare(self, timeout: int = 20) -> None:
        """Block until Cloudflare's JS challenge page clears.

        automationexercise.com is behind Cloudflare. In CI the challenge page
        ("Just a moment…") can appear for a few seconds before the real page
        loads. Waiting here keeps all subsequent waits from timing out against
        the challenge page instead of the real DOM.
        """
        try:
            self._wait(timeout).until(
                lambda d: "just a moment" not in d.title.lower()
                and "checking your browser" not in d.title.lower()
            )
        except TimeoutException:
            self.log.warning(
                "Cloudflare challenge did not clear within %ds — continuing anyway", timeout
            )

    def current_url(self) -> str:
        return self.driver.current_url

    def title(self) -> str:
        return self.driver.title

    # --- internal waits ---------------------------------------------------
    def _wait(self, timeout: Optional[int] = None) -> WebDriverWait:
        return WebDriverWait(self.driver, timeout or self.timeout)

    def find(self, locator: Locator, timeout: Optional[int] = None) -> WebElement:
        """Wait for presence and return the element."""
        self.log.debug("find %s", locator)
        return self._wait(timeout).until(EC.presence_of_element_located(locator))

    def find_visible(self, locator: Locator, timeout: Optional[int] = None) -> WebElement:
        return self._wait(timeout).until(EC.visibility_of_element_located(locator))

    # --- interactions -----------------------------------------------------
    def click(self, locator: Locator, timeout: Optional[int] = None) -> None:
        self.log.info("click %s", locator)
        element = self._wait(timeout).until(EC.element_to_be_clickable(locator))
        try:
            element.click()
        except ElementClickInterceptedException:
            # An overlay (often an ad) is covering the element — force it via JS.
            self.log.warning("click intercepted on %s, falling back to JS click", locator)
            self.driver.execute_script("arguments[0].click();", element)

    def type(self, locator: Locator, text: str, clear: bool = True,
             timeout: Optional[int] = None) -> None:
        self.log.info("type %r into %s", text, locator)
        element = self.find_visible(locator, timeout)
        if clear:
            element.clear()
        element.send_keys(text)

    def select_by_text(self, locator: Locator, text: str,
                       timeout: Optional[int] = None) -> None:
        self.log.info("select %r in %s", text, locator)
        Select(self.find_visible(locator, timeout)).select_by_visible_text(text)

    def get_text(self, locator: Locator, timeout: Optional[int] = None) -> str:
        text = self.find_visible(locator, timeout).text
        self.log.info("text of %s = %r", locator, text)
        return text

    def is_visible(self, locator: Locator, timeout: Optional[int] = None) -> bool:
        """Non-raising visibility check. Returns False on timeout."""
        try:
            self.find_visible(locator, timeout or 5)
            return True
        except TimeoutException:
            return False

    def scroll_into_view(self, locator: Locator, timeout: Optional[int] = None) -> WebElement:
        element = self.find(locator, timeout)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )
        return element

    def scroll_to_bottom(self) -> None:
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def scroll_to_top(self) -> None:
        self.driver.execute_script("window.scrollTo(0, 0);")

    def wait_for_scroll_top(self, timeout: Optional[int] = None) -> None:
        """Wait until the viewport has (smoothly) scrolled back to the top."""
        self._wait(timeout).until(
            lambda d: d.execute_script("return window.pageYOffset;") < 100
        )

    # --- waits exposed to page objects ------------------------------------
    def wait_for_url_contains(self, fragment: str, timeout: Optional[int] = None) -> bool:
        return self._wait(timeout).until(EC.url_contains(fragment))

    def wait_for_text(self, locator: Locator, text: str, timeout: Optional[int] = None) -> bool:
        return self._wait(timeout).until(
            EC.text_to_be_present_in_element(locator, text)
        )

    def count(self, locator: Locator) -> int:
        return len(self.driver.find_elements(*locator))

    # --- alerts -----------------------------------------------------------
    def accept_alert(self, timeout: Optional[int] = None) -> None:
        self.log.info("waiting for and accepting alert")
        self._wait(timeout).until(EC.alert_is_present())
        self.driver.switch_to.alert.accept()

    # --- best-effort consent / ad handling --------------------------------
    def dismiss_consent_if_present(self) -> None:
        """automationexercise.com serves Google consent / ad frames that can
        intercept clicks. This is best-effort and never fails the test."""
        from selenium.webdriver.common.by import By

        try:
            consent = self._wait(3).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(., 'Consent') or contains(., 'Accept')]")
                )
            )
            consent.click()
            self.log.info("dismissed a consent/ad dialog")
        except TimeoutException:
            pass
