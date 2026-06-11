"""Multi-page user flows shared by several tests and fixtures.

These deliberately live next to the tests (not in pages/): a flow strings
multiple page objects together, which is test-orchestration, not page
modelling.
"""
from selenium.webdriver.remote.webdriver import WebDriver

from pages.cart_page import CartModal, CartPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.products_page import ProductsPage
from pages.signup_page import SignupPage

# automationexercise.com accepts any card data — nothing is charged.
PAYMENT_CARD = {
    "name": "QA Bot",
    "number": "4242424242424242",
    "cvc": "311",
    "month": "12",
    "year": "2030",
}


def register_user(driver: WebDriver, user: dict) -> HomePage:
    """Full signup flow: from the login page to a logged-in home page."""
    login = LoginPage(driver).load()
    login.dismiss_consent_if_present()
    login.start_signup(user["name"], user["email"])

    signup = SignupPage(driver)
    assert signup.is_account_information_visible(), "'Enter Account Information' not shown"
    signup.fill_account_details(user)
    assert signup.account_created_visible(), "'ACCOUNT CREATED!' not shown"
    signup.click_continue()
    return HomePage(driver)


def delete_account(driver: WebDriver) -> None:
    """Delete the currently logged-in account and confirm the deletion page."""
    home = HomePage(driver)
    home.delete_account()
    signup = SignupPage(driver)
    assert signup.account_deleted_visible(), "'ACCOUNT DELETED!' not shown"
    signup.click_continue()


def add_first_product_to_cart(driver: WebDriver) -> str:
    """From anywhere: open the products page, add the first product, land on
    the cart page. Returns the product name."""
    products = ProductsPage(driver).load()
    products.dismiss_consent_if_present()
    name = products.add_to_cart(0)
    CartModal(driver).view_cart()
    return name


def checkout_and_pay(driver: WebDriver, comment: str = "Automated test order.") -> None:
    """From the cart page: proceed to checkout, place the order and pay."""
    from pages.checkout_page import CheckoutPage
    from pages.payment_page import PaymentPage

    cart = CartPage(driver)
    cart.proceed_to_checkout()
    checkout = CheckoutPage(driver)
    assert checkout.is_loaded(), "Checkout page (Address Details / Review Your Order) not shown"
    checkout.place_order(comment)

    payment = PaymentPage(driver)
    payment.pay_and_confirm(PAYMENT_CARD)
    assert payment.order_placed(), "'Order Placed!' confirmation not shown"
