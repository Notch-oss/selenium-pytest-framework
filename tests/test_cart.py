"""Cart behaviour (site test cases 11, 12, 13, 17, 20 and 22)."""
import pytest

from pages.cart_page import CartModal, CartPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.product_detail_page import ProductDetailPage
from pages.products_page import ProductsPage


@pytest.mark.smoke
def test_subscription_on_cart_page(driver):
    """TC 11: the footer subscription widget also works on the cart page."""
    CartPage(driver).load()
    # The footer is site-wide; HomePage doubles as the header/footer object.
    footer = HomePage(driver)
    footer.dismiss_consent_if_present()
    assert footer.is_visible(footer.SUBSCRIPTION_HEADING)

    footer.subscribe("qa.cart.subscriber@example.com")
    message = footer.subscription_success_message()
    assert "successfully subscribed" in message.lower(), (
        f"Unexpected subscription message: {message!r}"
    )


@pytest.mark.smoke
def test_add_products_to_cart(driver):
    """TC 12: two products end up in the cart with price, quantity and total."""
    products = ProductsPage(driver).load()
    products.dismiss_consent_if_present()

    first = products.add_to_cart(0)
    CartModal(driver).continue_shopping()
    second = products.add_to_cart(1)
    CartModal(driver).view_cart()

    cart = CartPage(driver)
    names = cart.item_names()
    assert len(names) == 2, f"Expected 2 cart rows, found {len(names)}: {names}"
    assert {first, second} == set(names)

    prices = cart.item_prices()
    quantities = cart.item_quantities()
    totals = cart.item_totals()
    assert quantities == [1, 1]
    assert totals == [p * q for p, q in zip(prices, quantities)], (
        f"Row totals {totals} do not match price x quantity {prices} x {quantities}"
    )


@pytest.mark.regression
def test_product_quantity_in_cart(driver):
    """TC 13: quantity chosen on the detail page is preserved in the cart."""
    home = HomePage(driver).load()
    home.dismiss_consent_if_present()
    home.view_first_product()

    detail = ProductDetailPage(driver)
    assert detail.is_loaded()
    detail.set_quantity(4)
    detail.add_to_cart()
    CartModal(driver).view_cart()

    cart = CartPage(driver)
    assert cart.item_quantities() == [4], (
        f"Expected quantity [4], got {cart.item_quantities()}"
    )


@pytest.mark.regression
def test_remove_product_from_cart(driver):
    """TC 17: the X button removes the product and empties the cart."""
    products = ProductsPage(driver).load()
    products.dismiss_consent_if_present()
    products.add_to_cart(0)
    CartModal(driver).view_cart()

    cart = CartPage(driver)
    assert cart.item_count() == 1
    cart.remove_item(0)
    assert cart.is_empty(), "Cart still shows items after removal"


@pytest.mark.regression
def test_search_products_and_verify_cart_after_login(driver, registered_user):
    """TC 20: searched products added as a guest survive logging in."""
    products = ProductsPage(driver).load()
    products.dismiss_consent_if_present()
    products.search("Blue Top")
    count = products.result_count()
    assert count > 0, "Search returned no products"

    added = []
    for index in range(count):
        added.append(products.add_to_cart(index))
        CartModal(driver).continue_shopping()

    header = HomePage(driver)
    header.go_to_cart()
    cart = CartPage(driver)
    assert sorted(cart.item_names()) == sorted(added)

    header.go_to_login()
    login = LoginPage(driver)
    login.login(registered_user["email"], registered_user["password"])
    assert header.is_logged_in()

    header.go_to_cart()
    assert sorted(cart.item_names()) == sorted(added), (
        "Cart contents changed after logging in"
    )


@pytest.mark.regression
def test_add_to_cart_from_recommended_items(driver):
    """TC 22: a product added from 'recommended items' appears in the cart."""
    home = HomePage(driver).load()
    home.dismiss_consent_if_present()

    home.scroll_to_bottom()
    assert home.is_visible(home.RECOMMENDED_TITLE), "'RECOMMENDED ITEMS' not visible"

    name = home.add_recommended_item_to_cart()
    CartModal(driver).view_cart()

    cart = CartPage(driver)
    assert name in cart.item_names(), (
        f"Recommended product {name!r} not in cart: {cart.item_names()}"
    )
