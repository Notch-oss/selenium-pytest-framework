"""Login scenarios — invalid cases data-driven from data/login_data.json,
valid login/logout against an account created by the registered_user fixture
(site test cases 2, 3 and 4)."""
import pytest

from pages.home_page import HomePage
from pages.login_page import LoginPage
from tests.flows import delete_account
from utils.data_loader import load_json

LOGIN_CASES = load_json("login_data.json")


@pytest.mark.smoke
@pytest.mark.parametrize("data", LOGIN_CASES, ids=[c["case"] for c in LOGIN_CASES])
def test_login_with_invalid_credentials(driver, data):
    """Invalid credentials must surface the site's error message and keep the
    user on the login page."""
    login = LoginPage(driver).load()
    login.dismiss_consent_if_present()
    login.login(data["email"], data["password"])

    error = login.login_error_message()
    assert data["expected_error"].lower() in error.lower(), (
        f"Expected error containing {data['expected_error']!r}, got {error!r}"
    )
    assert "login" in driver.current_url.lower()


@pytest.mark.smoke
def test_login_with_valid_credentials(driver, registered_user):
    """TC 2: valid login shows 'Logged in as <user>', then delete the account."""
    login = LoginPage(driver).load()
    login.dismiss_consent_if_present()
    login.login(registered_user["email"], registered_user["password"])

    home = HomePage(driver)
    assert home.is_logged_in(), "Header does not show 'Logged in as <user>'"
    assert registered_user["name"] == home.logged_in_username()

    delete_account(driver)


@pytest.mark.smoke
def test_logout_returns_to_login_page(driver, registered_user):
    """TC 4: logout drops the session and lands back on the login page."""
    login = LoginPage(driver).load()
    login.dismiss_consent_if_present()
    login.login(registered_user["email"], registered_user["password"])

    home = HomePage(driver)
    assert home.is_logged_in()
    home.logout()

    assert "/login" in driver.current_url
    assert login.is_visible(login.LOGIN_FORM_HEADING)
    assert not home.is_logged_in()
