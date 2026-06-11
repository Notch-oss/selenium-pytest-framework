"""Product detail page: https://automationexercise.com/product_details/<id>

Covers the product information block, the quantity selector and the
'Write Your Review' form.
"""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class ProductDetailPage(BasePage):
    NAME = (By.CSS_SELECTOR, ".product-information h2")
    CATEGORY = (By.XPATH, "//div[@class='product-information']/p[contains(text(),'Category')]")
    PRICE = (By.CSS_SELECTOR, ".product-information span span")
    AVAILABILITY = (By.XPATH, "//div[@class='product-information']//b[contains(text(),'Availability')]/..")
    CONDITION = (By.XPATH, "//div[@class='product-information']//b[contains(text(),'Condition')]/..")
    BRAND = (By.XPATH, "//div[@class='product-information']//b[contains(text(),'Brand')]/..")

    QUANTITY = (By.ID, "quantity")
    ADD_TO_CART = (By.CSS_SELECTOR, "button.cart")

    WRITE_REVIEW_LINK = (By.CSS_SELECTOR, "a[href='#reviews']")
    REVIEW_NAME = (By.ID, "name")
    REVIEW_EMAIL = (By.ID, "email")
    REVIEW_TEXT = (By.ID, "review")
    REVIEW_SUBMIT = (By.ID, "button-review")
    REVIEW_SUCCESS = (By.CSS_SELECTOR, "#review-section .alert-success span")

    def is_loaded(self) -> bool:
        return self.is_visible(self.NAME)

    # --- product information ----------------------------------------------
    def name(self) -> str:
        return self.get_text(self.NAME)

    def category_text(self) -> str:
        return self.get_text(self.CATEGORY)

    def price_text(self) -> str:
        return self.get_text(self.PRICE)

    def availability_text(self) -> str:
        return self.get_text(self.AVAILABILITY)

    def condition_text(self) -> str:
        return self.get_text(self.CONDITION)

    def brand_text(self) -> str:
        return self.get_text(self.BRAND)

    # --- cart ----------------------------------------------------------------
    def set_quantity(self, quantity: int) -> None:
        self.type(self.QUANTITY, str(quantity))

    def add_to_cart(self) -> None:
        self.click(self.ADD_TO_CART)

    # --- reviews ---------------------------------------------------------------
    def is_review_form_visible(self) -> bool:
        return self.is_visible(self.WRITE_REVIEW_LINK) and self.is_visible(self.REVIEW_TEXT)

    def submit_review(self, name: str, email: str, review: str) -> None:
        self.scroll_into_view(self.REVIEW_TEXT)
        self.type(self.REVIEW_NAME, name)
        self.type(self.REVIEW_EMAIL, email)
        self.type(self.REVIEW_TEXT, review)
        self.click(self.REVIEW_SUBMIT)

    def review_success_message(self) -> str:
        # The success banner auto-hides after a few seconds — read it promptly.
        return self.get_text(self.REVIEW_SUCCESS)
