"""Products page: https://automationexercise.com/products"""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class ProductsPage(BasePage):
    SEARCH_INPUT = (By.ID, "search_product")
    SEARCH_BUTTON = (By.ID, "submit_search")
    SEARCHED_PRODUCTS_TITLE = (By.XPATH, "//h2[contains(text(),'Searched Products')]")
    ALL_PRODUCTS_TITLE = (By.XPATH, "//h2[contains(text(),'All Products')]")
    PRODUCT_CARDS = (By.CSS_SELECTOR, ".features_items .product-image-wrapper")
    PRODUCT_NAMES = (By.CSS_SELECTOR, ".features_items .productinfo p")
    VIEW_PRODUCT_LINKS = (By.CSS_SELECTOR, ".features_items .choose a[href^='/product_details/']")
    # The non-overlay add-to-cart button; the overlay variant needs a hover,
    # which is flaky in headless runs.
    ADD_TO_CART_BUTTONS = (By.CSS_SELECTOR, ".features_items .productinfo a.add-to-cart")

    # Brands sidebar
    BRANDS_SIDEBAR = (By.CSS_SELECTOR, ".brands_products")
    BRAND_LINKS = (By.CSS_SELECTOR, ".brands_products .brands-name a")
    PAGE_TITLE = (By.CSS_SELECTOR, ".features_items h2.title")

    def load(self) -> "ProductsPage":
        self.open("/products")
        self.find_visible(self.ALL_PRODUCTS_TITLE)
        return self

    def search(self, term: str) -> None:
        self.type(self.SEARCH_INPUT, term)
        self.click(self.SEARCH_BUTTON)
        self.find_visible(self.SEARCHED_PRODUCTS_TITLE)

    def result_count(self) -> int:
        return self.count(self.PRODUCT_CARDS)

    def result_names(self) -> list[str]:
        return [e.text for e in self.driver.find_elements(*self.PRODUCT_NAMES)]

    # --- product cards ------------------------------------------------------
    def view_product(self, index: int = 0) -> None:
        links = self.driver.find_elements(*self.VIEW_PRODUCT_LINKS)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", links[index])
        links[index].click()
        self.wait_for_url_contains("/product_details/")

    def add_to_cart(self, index: int = 0) -> str:
        """Add the nth product card to the cart and return the product's name.

        Opens the 'Added!' modal — follow up with CartModal.continue_shopping()
        or CartModal.view_cart().
        """
        name = self.driver.find_elements(*self.PRODUCT_NAMES)[index].text
        button = self.driver.find_elements(*self.ADD_TO_CART_BUTTONS)[index]
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", button)
        # JS click: hovering the card raises an overlay that intercepts native clicks.
        self.driver.execute_script("arguments[0].click();", button)
        self.log.info("added product %r to cart", name)
        return name

    # --- brands ---------------------------------------------------------------
    def brands_visible(self) -> bool:
        return self.is_visible(self.BRANDS_SIDEBAR)

    def open_brand(self, index: int = 0) -> str:
        """Click the nth brand link in the sidebar and return the brand name."""
        link = self.driver.find_elements(*self.BRAND_LINKS)[index]
        brand = link.get_attribute("href").rstrip("/").split("/")[-1]
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", link)
        self.driver.execute_script("arguments[0].click();", link)
        self.wait_for_url_contains("/brand_products/")
        self.find_visible(self.PAGE_TITLE)
        return brand

    def page_title(self) -> str:
        return self.get_text(self.PAGE_TITLE)
