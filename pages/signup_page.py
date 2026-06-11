"""Signup / account lifecycle pages.

Covers the 'Enter Account Information' form reached after submitting the
'New User Signup!' form, plus the ACCOUNT CREATED and ACCOUNT DELETED
confirmation pages (they share the same 'Continue' button).

The user dict consumed by fill_account_details() comes from
utils.user_factory.new_user().
"""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class SignupPage(BasePage):
    HEADING = (By.XPATH, "//h2/b[contains(text(),'Enter Account Information')]")
    TITLE_MR = (By.ID, "id_gender1")
    PASSWORD = (By.CSS_SELECTOR, "input[data-qa='password']")
    BIRTH_DAY = (By.CSS_SELECTOR, "select[data-qa='days']")
    BIRTH_MONTH = (By.CSS_SELECTOR, "select[data-qa='months']")
    BIRTH_YEAR = (By.CSS_SELECTOR, "select[data-qa='years']")
    NEWSLETTER = (By.ID, "newsletter")
    SPECIAL_OFFERS = (By.ID, "optin")
    FIRST_NAME = (By.CSS_SELECTOR, "input[data-qa='first_name']")
    LAST_NAME = (By.CSS_SELECTOR, "input[data-qa='last_name']")
    COMPANY = (By.CSS_SELECTOR, "input[data-qa='company']")
    ADDRESS = (By.CSS_SELECTOR, "input[data-qa='address']")
    ADDRESS2 = (By.CSS_SELECTOR, "input[data-qa='address2']")
    COUNTRY = (By.CSS_SELECTOR, "select[data-qa='country']")
    STATE = (By.CSS_SELECTOR, "input[data-qa='state']")
    CITY = (By.CSS_SELECTOR, "input[data-qa='city']")
    ZIPCODE = (By.CSS_SELECTOR, "input[data-qa='zipcode']")
    MOBILE_NUMBER = (By.CSS_SELECTOR, "input[data-qa='mobile_number']")
    CREATE_ACCOUNT = (By.CSS_SELECTOR, "button[data-qa='create-account']")

    ACCOUNT_CREATED = (By.CSS_SELECTOR, "h2[data-qa='account-created']")
    ACCOUNT_DELETED = (By.CSS_SELECTOR, "h2[data-qa='account-deleted']")
    CONTINUE = (By.CSS_SELECTOR, "a[data-qa='continue-button']")

    def is_account_information_visible(self) -> bool:
        return self.is_visible(self.HEADING)

    def fill_account_details(self, user: dict) -> None:
        """Fill the whole account form from a user dict and submit it."""
        self.click(self.TITLE_MR)
        self.type(self.PASSWORD, user["password"])
        self.select_by_text(self.BIRTH_DAY, user["birth_day"])
        self.select_by_text(self.BIRTH_MONTH, user["birth_month"])
        self.select_by_text(self.BIRTH_YEAR, user["birth_year"])
        self.click(self.NEWSLETTER)
        self.click(self.SPECIAL_OFFERS)
        self.type(self.FIRST_NAME, user["first_name"])
        self.type(self.LAST_NAME, user["last_name"])
        self.type(self.COMPANY, user["company"])
        self.type(self.ADDRESS, user["address"])
        self.type(self.ADDRESS2, user["address2"])
        self.select_by_text(self.COUNTRY, user["country"])
        self.type(self.STATE, user["state"])
        self.type(self.CITY, user["city"])
        self.type(self.ZIPCODE, user["zipcode"])
        self.type(self.MOBILE_NUMBER, user["mobile_number"])
        self.click(self.CREATE_ACCOUNT)

    def account_created_visible(self) -> bool:
        return self.is_visible(self.ACCOUNT_CREATED, timeout=self.timeout)

    def account_deleted_visible(self) -> bool:
        return self.is_visible(self.ACCOUNT_DELETED, timeout=self.timeout)

    def click_continue(self) -> None:
        self.click(self.CONTINUE)
