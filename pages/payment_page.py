"""Payment page (https://automationexercise.com/payment) and the order
confirmation page it redirects to after a successful payment."""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class PaymentPage(BasePage):
    NAME_ON_CARD = (By.CSS_SELECTOR, "input[data-qa='name-on-card']")
    CARD_NUMBER = (By.CSS_SELECTOR, "input[data-qa='card-number']")
    CVC = (By.CSS_SELECTOR, "input[data-qa='cvc']")
    EXPIRY_MONTH = (By.CSS_SELECTOR, "input[data-qa='expiry-month']")
    EXPIRY_YEAR = (By.CSS_SELECTOR, "input[data-qa='expiry-year']")
    PAY_BUTTON = (By.CSS_SELECTOR, "button[data-qa='pay-button']")

    # Confirmation page (/payment_done/<order id>)
    ORDER_PLACED_HEADING = (By.CSS_SELECTOR, "h2[data-qa='order-placed']")
    DOWNLOAD_INVOICE = (By.CSS_SELECTOR, "a[href^='/download_invoice']")
    CONTINUE = (By.CSS_SELECTOR, "a[data-qa='continue-button']")

    def pay_and_confirm(self, card: dict) -> None:
        self.type(self.NAME_ON_CARD, card["name"])
        self.type(self.CARD_NUMBER, card["number"])
        self.type(self.CVC, card["cvc"])
        self.type(self.EXPIRY_MONTH, card["month"])
        self.type(self.EXPIRY_YEAR, card["year"])
        self.click(self.PAY_BUTTON)
        # The success flash is transient; the stable signal is the redirect to
        # the confirmation page with its 'Order Placed!' heading.
        self.wait_for_url_contains("/payment_done")

    def order_placed(self) -> bool:
        return self.is_visible(self.ORDER_PLACED_HEADING, timeout=self.timeout)

    def download_invoice(self) -> None:
        self.click(self.DOWNLOAD_INVOICE)

    def click_continue(self) -> None:
        self.click(self.CONTINUE)
