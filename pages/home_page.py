"""Home page: https://automationexercise.com/

Covers the top navigation, the footer subscription widget, the hero carousel,
the category sidebar and the 'recommended items' carousel.

The header and footer are identical on every page of the site, so tests on
other pages reuse HomePage (without calling load()) for header/footer actions
such as logout, delete-account or subscribing.
"""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class HomePage(BasePage):
    # Navigation
    NAV_SIGNUP_LOGIN = (By.CSS_SELECTOR, "a[href='/login']")
    NAV_PRODUCTS = (By.CSS_SELECTOR, "a[href='/products']")
    NAV_CONTACT_US = (By.CSS_SELECTOR, "a[href='/contact_us']")
    NAV_CART = (By.CSS_SELECTOR, ".shop-menu a[href='/view_cart']")
    NAV_TEST_CASES = (By.CSS_SELECTOR, ".shop-menu a[href='/test_cases']")
    NAV_LOGOUT = (By.CSS_SELECTOR, "a[href='/logout']")
    NAV_DELETE_ACCOUNT = (By.CSS_SELECTOR, "a[href='/delete_account']")
    LOGGED_IN_AS = (By.XPATH, "//ul[contains(@class,'navbar-nav')]//a[contains(., 'Logged in as')]")

    # Hero carousel
    SLIDER = (By.ID, "slider")
    CAROUSEL_HEADING = (By.CSS_SELECTOR, "#slider-carousel .item.active h2")
    SCROLL_UP_ARROW = (By.ID, "scrollUp")

    # Footer subscription (note: the site's input id is misspelled "susbscribe")
    SUBSCRIBE_EMAIL = (By.ID, "susbscribe_email")
    SUBSCRIBE_BUTTON = (By.ID, "subscribe")
    SUBSCRIBE_SUCCESS = (By.ID, "success-subscribe")
    SUBSCRIPTION_HEADING = (By.XPATH, "//footer//h2[contains(text(),'Subscription')]")

    # Left sidebar categories (also present on the products page)
    CATEGORY_SIDEBAR = (By.CSS_SELECTOR, ".left-sidebar .category-products")
    CATEGORY_TITLE = (By.CSS_SELECTOR, ".features_items h2.title")

    # Product grid on the home page
    VIEW_PRODUCT_LINKS = (By.CSS_SELECTOR, ".features_items .choose a[href^='/product_details/']")

    # Recommended items carousel at the bottom of the home page
    RECOMMENDED_TITLE = (By.XPATH, "//h2[contains(text(),'recommended items')]")
    RECOMMENDED_ACTIVE_ITEM = (By.CSS_SELECTOR, "#recommended-item-carousel .item.active")

    def load(self) -> "HomePage":
        self.open("/")
        self.find_visible(self.SLIDER)
        return self

    def is_loaded(self) -> bool:
        return self.is_visible(self.SLIDER)

    # --- header -------------------------------------------------------------
    def go_to_login(self) -> None:
        self.click(self.NAV_SIGNUP_LOGIN)

    def go_to_products(self) -> None:
        self.click(self.NAV_PRODUCTS)

    def go_to_contact_us(self) -> None:
        self.click(self.NAV_CONTACT_US)

    def go_to_cart(self) -> None:
        self.click(self.NAV_CART)

    def go_to_test_cases(self) -> None:
        self.click(self.NAV_TEST_CASES)

    def is_logged_in(self) -> bool:
        return self.is_visible(self.LOGGED_IN_AS)

    def logged_in_username(self) -> str:
        """Returns the username from the 'Logged in as <name>' header link."""
        return self.get_text(self.LOGGED_IN_AS).replace("Logged in as", "").strip()

    def logout(self) -> None:
        self.click(self.NAV_LOGOUT)
        self.wait_for_url_contains("/login")

    def delete_account(self) -> None:
        self.click(self.NAV_DELETE_ACCOUNT)

    # --- footer subscription --------------------------------------------------
    def subscribe(self, email: str) -> None:
        self.scroll_into_view(self.SUBSCRIBE_EMAIL)
        self.type(self.SUBSCRIBE_EMAIL, email)
        self.click(self.SUBSCRIBE_BUTTON)

    def subscription_success_message(self) -> str:
        return self.get_text(self.SUBSCRIBE_SUCCESS)

    # --- categories -----------------------------------------------------------
    def open_category(self, category: str, sub_category: str) -> None:
        """Expand a sidebar category panel (e.g. 'Women') and open one of its
        sub-category links (e.g. 'Dress')."""
        self.scroll_into_view(self.CATEGORY_SIDEBAR)
        self.click((By.CSS_SELECTOR, f".category-products a[href='#{category}']"))
        self.click((By.XPATH, f"//div[@id='{category}']//a[contains(text(),'{sub_category}')]"))
        self.find_visible(self.CATEGORY_TITLE)

    def category_title(self) -> str:
        return self.get_text(self.CATEGORY_TITLE)

    # --- products on the home page ---------------------------------------------
    def view_first_product(self) -> None:
        self.scroll_into_view(self.VIEW_PRODUCT_LINKS)
        self.click(self.VIEW_PRODUCT_LINKS)
        self.wait_for_url_contains("/product_details/")

    def add_recommended_item_to_cart(self) -> str:
        """Add the currently visible recommended product and return its name.

        Name and add-to-cart link are read from the same carousel item element,
        so the result stays consistent even if the carousel rotates afterwards.
        """
        self.scroll_into_view(self.RECOMMENDED_TITLE)
        item = self.find_visible(self.RECOMMENDED_ACTIVE_ITEM)
        name = item.find_element(By.CSS_SELECTOR, ".productinfo p").text
        add_link = item.find_element(By.CSS_SELECTOR, ".productinfo a.add-to-cart")
        # JS click: the carousel may animate mid-click, which breaks native clicks.
        self.driver.execute_script("arguments[0].click();", add_link)
        return name

    # --- scroll behaviour --------------------------------------------------------
    def click_scroll_up_arrow(self) -> None:
        self.click(self.SCROLL_UP_ARROW)

    def carousel_heading_text(self) -> str:
        return self.get_text(self.CAROUSEL_HEADING)
