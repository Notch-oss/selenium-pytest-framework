"""Login / Signup page: https://automationexercise.com/login

Holds both the 'Login to your account' form and the 'New User Signup!' form.
"""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LoginPage(BasePage):
    # Login form
    LOGIN_EMAIL = (By.CSS_SELECTOR, "input[data-qa='login-email']")
    LOGIN_PASSWORD = (By.CSS_SELECTOR, "input[data-qa='login-password']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[data-qa='login-button']")
    LOGIN_ERROR = (By.CSS_SELECTOR, ".login-form p")

    # Signup form
    SIGNUP_NAME = (By.CSS_SELECTOR, "input[data-qa='signup-name']")
    SIGNUP_EMAIL = (By.CSS_SELECTOR, "input[data-qa='signup-email']")
    SIGNUP_BUTTON = (By.CSS_SELECTOR, "button[data-qa='signup-button']")
    SIGNUP_ERROR = (By.CSS_SELECTOR, ".signup-form p")

    LOGIN_FORM_HEADING = (By.XPATH, "//h2[contains(text(),'Login to your account')]")
    SIGNUP_FORM_HEADING = (By.XPATH, "//h2[contains(text(),'New User Signup!')]")

    def load(self) -> "LoginPage":
        self.open("/login")
        self.find_visible(self.LOGIN_FORM_HEADING)
        return self

    def login(self, email: str, password: str) -> None:
        self.type(self.LOGIN_EMAIL, email)
        self.type(self.LOGIN_PASSWORD, password)
        self.click(self.LOGIN_BUTTON)

    def login_error_message(self) -> str:
        return self.get_text(self.LOGIN_ERROR)

    def start_signup(self, name: str, email: str) -> None:
        self.type(self.SIGNUP_NAME, name)
        self.type(self.SIGNUP_EMAIL, email)
        self.click(self.SIGNUP_BUTTON)

    def signup_error_message(self) -> str:
        return self.get_text(self.SIGNUP_ERROR)
