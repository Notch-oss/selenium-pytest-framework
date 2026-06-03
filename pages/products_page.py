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
