"""Client for the AutomationExercise public REST API.

One method per endpoint documented at https://automationexercise.com/api_list
(APIs 1-14). Methods reveal intent and hide HTTP details; they return an
`ApiResponse` whose `response_code` carries the API's real status code (see
`base_client` for why that does not equal the HTTP status line).

Account-mutating endpoints (create/update) take a `user` dict already keyed by
the exact API form-field names — build it with `utils.user_factory.new_api_user`.
"""
from __future__ import annotations

from api.base_client import ApiResponse, BaseApiClient


class AutomationExerciseApiClient(BaseApiClient):
    # Endpoint paths, relative to Config.API_BASE_URL.
    PRODUCTS_LIST = "productsList"
    BRANDS_LIST = "brandsList"
    SEARCH_PRODUCT = "searchProduct"
    VERIFY_LOGIN = "verifyLogin"
    CREATE_ACCOUNT = "createAccount"
    DELETE_ACCOUNT = "deleteAccount"
    UPDATE_ACCOUNT = "updateAccount"
    USER_DETAIL_BY_EMAIL = "getUserDetailByEmail"

    # --- Products -------------------------------------------------------
    def get_all_products(self) -> ApiResponse:
        """API 1 — GET all products (expects responseCode 200, `products` list)."""
        return self.get(self.PRODUCTS_LIST)

    def post_all_products(self) -> ApiResponse:
        """API 2 — POST to the products list, an unsupported method
        (expects responseCode 405)."""
        return self.post(self.PRODUCTS_LIST)

    # --- Brands ---------------------------------------------------------
    def get_all_brands(self) -> ApiResponse:
        """API 3 — GET all brands (expects responseCode 200, `brands` list)."""
        return self.get(self.BRANDS_LIST)

    def put_all_brands(self) -> ApiResponse:
        """API 4 — PUT to the brands list, an unsupported method
        (expects responseCode 405)."""
        return self.put(self.BRANDS_LIST)

    # --- Search ---------------------------------------------------------
    def search_product(self, search_term: str) -> ApiResponse:
        """API 5 — POST search for products by term (expects responseCode 200)."""
        return self.post(self.SEARCH_PRODUCT, data={"search_product": search_term})

    def search_product_without_param(self) -> ApiResponse:
        """API 6 — POST search with the `search_product` field omitted
        (expects responseCode 400)."""
        return self.post(self.SEARCH_PRODUCT)

    # --- Verify login ---------------------------------------------------
    def verify_login(self, email: str, password: str) -> ApiResponse:
        """API 7 / API 10 — POST verify a login. Valid credentials return
        responseCode 200 ('User exists!'); unknown credentials return 404."""
        return self.post(self.VERIFY_LOGIN, data={"email": email, "password": password})

    def verify_login_without_email(self, password: str) -> ApiResponse:
        """API 8 — POST verify login with the `email` field omitted
        (expects responseCode 400)."""
        return self.post(self.VERIFY_LOGIN, data={"password": password})

    def verify_login_via_delete(self) -> ApiResponse:
        """API 9 — DELETE against verifyLogin, an unsupported method
        (expects responseCode 405)."""
        return self.delete(self.VERIFY_LOGIN)

    # --- Account lifecycle ---------------------------------------------
    def create_account(self, user: dict) -> ApiResponse:
        """API 11 — POST create/register a user account
        (expects responseCode 201, 'User created!'). `user` must be keyed by the
        API form-field names (see utils.user_factory.new_api_user)."""
        return self.post(self.CREATE_ACCOUNT, data=user)

    def delete_account(self, email: str, password: str) -> ApiResponse:
        """API 12 — DELETE a user account (expects responseCode 200,
        'Account deleted!'; a missing account returns 404)."""
        return self.delete(self.DELETE_ACCOUNT, data={"email": email, "password": password})

    def update_account(self, user: dict) -> ApiResponse:
        """API 13 — PUT update an existing user account
        (expects responseCode 200, 'User updated!')."""
        return self.put(self.UPDATE_ACCOUNT, data=user)

    def get_user_detail_by_email(self, email: str) -> ApiResponse:
        """API 14 — GET a user's account detail by email
        (expects responseCode 200, `user` object)."""
        return self.get(self.USER_DETAIL_BY_EMAIL, params={"email": email})
