"""Product browsing: detail page, categories, brands, reviews
(site test cases 8, 18, 19 and 21)."""
import pytest

from pages.home_page import HomePage
from pages.product_detail_page import ProductDetailPage
from pages.products_page import ProductsPage


@pytest.mark.smoke
def test_all_products_and_product_detail(driver):
    """TC 8: products list is visible and the detail page shows name,
    category, price, availability, condition and brand."""
    products = ProductsPage(driver).load()
    products.dismiss_consent_if_present()
    assert products.result_count() > 0, "No products listed on the All Products page"

    products.view_product(0)
    detail = ProductDetailPage(driver)
    assert detail.is_loaded()
    assert detail.name(), "Product name missing"
    assert "category" in detail.category_text().lower()
    assert "rs." in detail.price_text().lower()
    assert "in stock" in detail.availability_text().lower()
    assert "condition" in detail.condition_text().lower()
    assert "brand" in detail.brand_text().lower()


@pytest.mark.regression
def test_view_category_products(driver):
    """TC 18: sidebar categories navigate to the matching category pages."""
    home = HomePage(driver).load()
    home.dismiss_consent_if_present()
    assert home.is_visible(home.CATEGORY_SIDEBAR), "Category sidebar not visible"

    home.open_category("Women", "Dress")
    assert "women - dress products" in home.category_title().lower()

    home.open_category("Men", "Tshirts")
    assert "men - tshirts products" in home.category_title().lower()


@pytest.mark.regression
def test_view_brand_products(driver):
    """TC 19: sidebar brands navigate to the matching brand pages."""
    products = ProductsPage(driver).load()
    products.dismiss_consent_if_present()
    assert products.brands_visible(), "Brands sidebar not visible"

    first_brand = products.open_brand(0)
    assert first_brand.lower() in products.page_title().lower()
    assert products.result_count() > 0, f"No products shown for brand {first_brand!r}"

    second_brand = products.open_brand(1)
    assert second_brand.lower() in products.page_title().lower()
    assert products.result_count() > 0, f"No products shown for brand {second_brand!r}"


@pytest.mark.regression
def test_add_review_on_product(driver):
    """TC 21: submitting a product review shows the thank-you banner."""
    products = ProductsPage(driver).load()
    products.dismiss_consent_if_present()
    products.view_product(0)

    detail = ProductDetailPage(driver)
    assert detail.is_review_form_visible(), "'Write Your Review' form not visible"
    detail.submit_review(
        name="QA Bot",
        email="qa.bot@example.com",
        review="Automated review submitted by the Selenium test suite.",
    )
    message = detail.review_success_message()
    assert "thank you for your review" in message.lower(), (
        f"Unexpected review confirmation: {message!r}"
    )
