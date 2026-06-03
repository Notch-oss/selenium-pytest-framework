"""Home page: https://automationexercise.com/

Covers the top navigation and the footer subscription widget.
"""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class HomePage(BasePage):
    # Navigation
    NAV_SIGNUP_LOGIN = (By.CSS_SELECTOR, "a[href='/login']")
    NAV_PRODUCTS = (By.CSS_SELECTOR, "a[href='/products']")
    NAV_CONTACT_US = (By.CSS_SELECTOR, "a[href='/contact_us']")
    SLIDER = (By.ID, "slider")

    # Footer subscription (note: the site's input id is misspelled "susbscribe")
    SUBSCRIBE_EMAIL = (By.ID, "susbscribe_email")
    SUBSCRIBE_BUTTON = (By.ID, "subscribe")
    SUBSCRIBE_SUCCESS = (By.ID, "success-subscribe")

    def load(self) -> "HomePage":
        self.open("/")
        self.find_visible(self.SLIDER)
        return self

    def is_loaded(self) -> bool:
        return self.is_visible(self.SLIDER)

    def go_to_login(self) -> None:
        self.click(self.NAV_SIGNUP_LOGIN)

    def go_to_products(self) -> None:
        self.click(self.NAV_PRODUCTS)

    def go_to_contact_us(self) -> None:
        self.click(self.NAV_CONTACT_US)

    def subscribe(self, email: str) -> None:
        self.scroll_into_view(self.SUBSCRIBE_EMAIL)
        self.type(self.SUBSCRIBE_EMAIL, email)
        self.click(self.SUBSCRIBE_BUTTON)

    def subscription_success_message(self) -> str:
        return self.get_text(self.SUBSCRIBE_SUCCESS)
