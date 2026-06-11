"""Cart page (https://automationexercise.com/view_cart) and the 'Added!'
modal that pops up after every add-to-cart action."""
import re
from typing import Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage


def _rupees(text: str) -> int:
    """'Rs. 500' -> 500."""
    return int(re.sub(r"[^\d]", "", text))


class CartModal(BasePage):
    """The modal shown after adding a product to the cart, from any page."""
    MODAL = (By.ID, "cartModal")
    CONTINUE_SHOPPING = (By.CSS_SELECTOR, "#cartModal .close-modal")
    VIEW_CART = (By.CSS_SELECTOR, "#cartModal a[href='/view_cart']")

    def continue_shopping(self) -> None:
        self.click(self.CONTINUE_SHOPPING)
        self._wait().until(EC.invisibility_of_element_located(self.MODAL))

    def view_cart(self) -> None:
        self.click(self.VIEW_CART)
        self.wait_for_url_contains("/view_cart")


class CartPage(BasePage):
    ROWS = (By.CSS_SELECTOR, "#cart_info_table tbody tr[id^='product-']")
    NAMES = (By.CSS_SELECTOR, "#cart_info_table .cart_description h4 a")
    PRICES = (By.CSS_SELECTOR, "#cart_info_table .cart_price p")
    QUANTITIES = (By.CSS_SELECTOR, "#cart_info_table .cart_quantity button")
    TOTALS = (By.CSS_SELECTOR, "#cart_info_table .cart_total .cart_total_price")
    DELETE_BUTTONS = (By.CSS_SELECTOR, "#cart_info_table .cart_quantity_delete")
    EMPTY_CART = (By.ID, "empty_cart")

    PROCEED_TO_CHECKOUT = (By.CSS_SELECTOR, "a.check_out")
    # Shown instead of checkout when the visitor is not logged in.
    CHECKOUT_MODAL_REGISTER_LOGIN = (By.CSS_SELECTOR, "#checkoutModal a[href='/login']")

    def load(self) -> "CartPage":
        self.open("/view_cart")
        return self

    # --- contents -----------------------------------------------------------
    def item_count(self) -> int:
        return self.count(self.ROWS)

    def item_names(self) -> list[str]:
        return [e.text for e in self.driver.find_elements(*self.NAMES)]

    def item_prices(self) -> list[int]:
        return [_rupees(e.text) for e in self.driver.find_elements(*self.PRICES)]

    def item_quantities(self) -> list[int]:
        return [int(e.text) for e in self.driver.find_elements(*self.QUANTITIES)]

    def item_totals(self) -> list[int]:
        return [_rupees(e.text) for e in self.driver.find_elements(*self.TOTALS)]

    def is_empty(self, timeout: Optional[int] = None) -> bool:
        return self.is_visible(self.EMPTY_CART, timeout)

    # --- actions ----------------------------------------------------------------
    def remove_item(self, index: int = 0) -> None:
        rows_before = self.item_count()
        self.driver.find_elements(*self.DELETE_BUTTONS)[index].click()
        # Removal is an async XHR; wait for the row to disappear.
        self._wait().until(
            lambda d: self.item_count() < rows_before
            or d.find_element(*self.EMPTY_CART).is_displayed()
        )

    def proceed_to_checkout(self) -> None:
        self.scroll_into_view(self.PROCEED_TO_CHECKOUT)
        self.click(self.PROCEED_TO_CHECKOUT)

    def register_login_from_modal(self) -> None:
        """In the 'Checkout' modal shown to anonymous visitors, follow the
        Register / Login link."""
        self.click(self.CHECKOUT_MODAL_REGISTER_LOGIN)
        self.wait_for_url_contains("/login")
