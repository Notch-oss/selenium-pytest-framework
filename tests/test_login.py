"""Login scenarios — data-driven from data/login_data.json."""
import pytest

from pages.login_page import LoginPage
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
