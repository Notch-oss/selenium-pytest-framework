"""Contact Us form submission, including the native confirm() dialog."""
import pytest

from pages.contact_page import ContactPage


@pytest.mark.regression
def test_contact_us_form_submission(driver):
    contact = ContactPage(driver).load()
    contact.dismiss_consent_if_present()
    contact.submit_form(
        name="QA Bot",
        email="qa.bot@example.com",
        subject="Automated framework smoke check",
        message="This message was submitted by an automated Selenium test.",
    )

    message = contact.success_message()
    assert "submitted successfully" in message.lower(), (
        f"Unexpected contact-us message: {message!r}"
    )
