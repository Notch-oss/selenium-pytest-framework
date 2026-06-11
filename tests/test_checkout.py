"""End-to-end order placement (site test cases 14, 15, 16, 23 and 24)."""
import pytest
from selenium.webdriver.support.ui import WebDriverWait

from pages.cart_page import CartModal, CartPage
from pages.checkout_page import CheckoutPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.payment_page import PaymentPage
from pages.signup_page import SignupPage
from tests.flows import (
    PAYMENT_CARD,
    add_first_product_to_cart,
    checkout_and_pay,
    delete_account,
    register_user,
)
from utils.user_factory import new_user


@pytest.mark.regression
def test_place_order_register_while_checkout(driver):
    """TC 14: an anonymous shopper registers mid-checkout and completes the order."""
    user = new_user()
    add_first_product_to_cart(driver)

    cart = CartPage(driver)
    assert cart.item_count() == 1
    cart.proceed_to_checkout()
    cart.register_login_from_modal()

    login = LoginPage(driver)
    login.start_signup(user["name"], user["email"])
    signup = SignupPage(driver)
    signup.fill_account_details(user)
    assert signup.account_created_visible()
    signup.click_continue()

    home = HomePage(driver)
    assert home.is_logged_in()
    home.go_to_cart()
    checkout_and_pay(driver)

    delete_account(driver)


@pytest.mark.regression
def test_place_order_register_before_checkout(driver):
    """TC 15: register first, then shop and complete the order."""
    user = new_user()
    home = register_user(driver, user)
    assert home.is_logged_in()

    add_first_product_to_cart(driver)
    assert CartPage(driver).item_count() == 1
    checkout_and_pay(driver)

    delete_account(driver)


@pytest.mark.regression
def test_place_order_login_before_checkout(driver, registered_user):
    """TC 16: log into an existing account, then shop and complete the order."""
    login = LoginPage(driver).load()
    login.dismiss_consent_if_present()
    login.login(registered_user["email"], registered_user["password"])
    home = HomePage(driver)
    assert home.is_logged_in()

    add_first_product_to_cart(driver)
    assert CartPage(driver).item_count() == 1
    checkout_and_pay(driver)

    delete_account(driver)


@pytest.mark.regression
def test_address_details_match_registration(driver):
    """TC 23: checkout delivery and billing addresses echo the registration data."""
    user = new_user()
    home = register_user(driver, user)
    assert home.is_logged_in()

    add_first_product_to_cart(driver)
    CartPage(driver).proceed_to_checkout()

    checkout = CheckoutPage(driver)
    assert checkout.is_loaded()

    expected_fragments = [
        f"{user['first_name']} {user['last_name']}",
        user["company"],
        user["address"],
        user["address2"],
        user["city"],
        user["state"],
        user["zipcode"],
        user["country"],
        user["mobile_number"],
    ]
    for label, lines in (
        ("delivery", checkout.delivery_address_lines()),
        ("billing", checkout.billing_address_lines()),
    ):
        blob = " ".join(lines)
        for fragment in expected_fragments:
            assert fragment in blob, (
                f"{label} address is missing {fragment!r}. Shown: {lines}"
            )

    delete_account(driver)


@pytest.mark.regression
def test_download_invoice_after_purchase(driver, tmp_path):
    """TC 24: the confirmation page offers an invoice that actually downloads."""
    user = new_user()
    home = register_user(driver, user)
    assert home.is_logged_in()

    add_first_product_to_cart(driver)

    cart = CartPage(driver)
    cart.proceed_to_checkout()
    checkout = CheckoutPage(driver)
    assert checkout.is_loaded()
    checkout.place_order("Automated invoice-download test order.")

    payment = PaymentPage(driver)
    payment.pay_and_confirm(PAYMENT_CARD)
    assert payment.order_placed()
    assert payment.is_visible(payment.DOWNLOAD_INVOICE), "'Download Invoice' button missing"

    if hasattr(driver, "execute_cdp_cmd"):  # Chrome: verify the file really lands.
        driver.execute_cdp_cmd(
            "Page.setDownloadBehavior",
            {"behavior": "allow", "downloadPath": str(tmp_path)},
        )
        payment.download_invoice()
        WebDriverWait(driver, 15).until(
            lambda _: any(f.stat().st_size > 0 for f in tmp_path.iterdir())
        )

    payment.click_continue()
    delete_account(driver)
