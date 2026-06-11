"""User registration scenarios (site test cases 1 and 5)."""
import pytest

from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.signup_page import SignupPage
from tests.flows import delete_account
from utils.user_factory import new_user


@pytest.mark.smoke
def test_register_new_user(driver):
    """TC 1: full signup flow ending with account deletion."""
    user = new_user()
    home = HomePage(driver).load()
    home.dismiss_consent_if_present()
    assert home.is_loaded()

    home.go_to_login()
    login = LoginPage(driver)
    assert login.is_visible(login.SIGNUP_FORM_HEADING), "'New User Signup!' not visible"
    login.start_signup(user["name"], user["email"])

    signup = SignupPage(driver)
    assert signup.is_account_information_visible(), "'Enter Account Information' not visible"
    signup.fill_account_details(user)
    assert signup.account_created_visible(), "'ACCOUNT CREATED!' not visible"
    signup.click_continue()

    assert home.is_logged_in(), "Header does not show 'Logged in as <user>'"
    assert user["name"] == home.logged_in_username()

    delete_account(driver)


@pytest.mark.regression
def test_register_with_existing_email_shows_error(driver, registered_user):
    """TC 5: signing up with an already-registered email must be rejected."""
    login = LoginPage(driver).load()
    login.dismiss_consent_if_present()
    login.start_signup("Another Name", registered_user["email"])

    error = login.signup_error_message()
    assert "email address already exist" in error.lower(), (
        f"Expected 'Email Address already exist!' error, got {error!r}"
    )
