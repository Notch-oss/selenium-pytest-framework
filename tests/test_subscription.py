"""Footer newsletter subscription on the home page."""
import pytest

from pages.home_page import HomePage


@pytest.mark.smoke
def test_footer_subscription_shows_success(driver):
    home = HomePage(driver).load()
    home.dismiss_consent_if_present()
    home.subscribe("qa.subscriber@example.com")

    message = home.subscription_success_message()
    assert "successfully subscribed" in message.lower(), (
        f"Unexpected subscription message: {message!r}"
    )
