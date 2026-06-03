"""Contact Us page: https://automationexercise.com/contact_us

Submitting the form triggers a native JS confirm() dialog that must be
accepted before the success banner appears.
"""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class ContactPage(BasePage):
    NAME = (By.CSS_SELECTOR, "input[data-qa='name']")
    EMAIL = (By.CSS_SELECTOR, "input[data-qa='email']")
    SUBJECT = (By.CSS_SELECTOR, "input[data-qa='subject']")
    MESSAGE = (By.CSS_SELECTOR, "textarea[data-qa='message']")
    SUBMIT = (By.CSS_SELECTOR, "input[data-qa='submit-button']")
    SUCCESS = (By.CSS_SELECTOR, ".status.alert-success")
    HEADING = (By.XPATH, "//h2[contains(text(),'Get In Touch')]")

    def load(self) -> "ContactPage":
        self.open("/contact_us")
        self.find_visible(self.HEADING)
        return self

    def submit_form(self, name: str, email: str, subject: str, message: str) -> None:
        self.type(self.NAME, name)
        self.type(self.EMAIL, email)
        self.type(self.SUBJECT, subject)
        self.type(self.MESSAGE, message)
        self.click(self.SUBMIT)
        # Native "Press OK to proceed!" confirm dialog.
        self.accept_alert()

    def success_message(self) -> str:
        return self.get_text(self.SUCCESS)
