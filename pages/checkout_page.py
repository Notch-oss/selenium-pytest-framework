"""Checkout page: https://automationexercise.com/checkout

Shows delivery/billing address blocks, an order review table and the comment
box, then hands off to the payment page.
"""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CheckoutPage(BasePage):
    ADDRESS_DETAILS_HEADING = (By.XPATH, "//h2[contains(text(),'Address Details')]")
    REVIEW_ORDER_HEADING = (By.XPATH, "//h2[contains(text(),'Review Your Order')]")
    DELIVERY_ADDRESS = (By.ID, "address_delivery")
    BILLING_ADDRESS = (By.ID, "address_invoice")
    COMMENT = (By.NAME, "message")
    PLACE_ORDER = (By.CSS_SELECTOR, "a[href='/payment']")

    def is_loaded(self) -> bool:
        return (self.is_visible(self.ADDRESS_DETAILS_HEADING)
                and self.is_visible(self.REVIEW_ORDER_HEADING))

    def _address_lines(self, locator) -> list[str]:
        block = self.find_visible(locator)
        items = block.find_elements(By.TAG_NAME, "li")
        # Skip the first <li>: it is the "Your delivery/billing address" title.
        return [li.text.strip() for li in items[1:] if li.text.strip()]

    def delivery_address_lines(self) -> list[str]:
        return self._address_lines(self.DELIVERY_ADDRESS)

    def billing_address_lines(self) -> list[str]:
        return self._address_lines(self.BILLING_ADDRESS)

    def place_order(self, comment: str = "") -> None:
        if comment:
            self.scroll_into_view(self.COMMENT)
            self.type(self.COMMENT, comment)
        self.scroll_into_view(self.PLACE_ORDER)
        self.click(self.PLACE_ORDER)
        self.wait_for_url_contains("/payment")
