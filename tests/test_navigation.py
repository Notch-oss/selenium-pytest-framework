"""Navigation and scroll behaviour (site test cases 7, 25 and 26)."""
import pytest
from selenium.webdriver.common.by import By

from pages.home_page import HomePage

CAROUSEL_TEXT = "Full-Fledged practice website for Automation Engineers"
TEST_CASES_HEADING = (By.XPATH, "//h2[contains(., 'Test Cases')]")


@pytest.mark.smoke
def test_test_cases_page_is_reachable(driver):
    """TC 7: the 'Test Cases' header link navigates to the test cases page."""
    home = HomePage(driver).load()
    home.dismiss_consent_if_present()
    home.go_to_test_cases()

    home.wait_for_url_contains("/test_cases")
    assert home.is_visible(TEST_CASES_HEADING), "Test Cases page heading not visible"


@pytest.mark.regression
def test_scroll_up_with_arrow_button(driver):
    """TC 25: the bottom-right arrow scrolls back to the hero carousel."""
    home = HomePage(driver).load()
    home.dismiss_consent_if_present()

    home.scroll_to_bottom()
    assert home.is_visible(home.SUBSCRIPTION_HEADING), "'SUBSCRIPTION' not visible in footer"

    home.click_scroll_up_arrow()
    home.wait_for_scroll_top()
    assert CAROUSEL_TEXT.lower() in home.carousel_heading_text().lower()


@pytest.mark.regression
def test_scroll_up_without_arrow_button(driver):
    """TC 26: scrolling up via the window itself reveals the hero carousel."""
    home = HomePage(driver).load()
    home.dismiss_consent_if_present()

    home.scroll_to_bottom()
    assert home.is_visible(home.SUBSCRIPTION_HEADING), "'SUBSCRIPTION' not visible in footer"

    home.scroll_to_top()
    home.wait_for_scroll_top()
    assert CAROUSEL_TEXT.lower() in home.carousel_heading_text().lower()
