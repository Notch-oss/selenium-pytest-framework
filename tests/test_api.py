"""REST API tests for the AutomationExercise public API (APIs 1-14).

Source of truth: https://automationexercise.com/api_list

All 14 documented endpoints are covered, each asserting the documented
`responseCode` and message exactly as the live API returns them. Tests talk to
`AutomationExerciseApiClient` (the `api` fixture), never to `requests` directly.

The API's defining quirk — verified against the live service — is that the
transport HTTP status is **always 200**; the real status code is carried in the
JSON body as `responseCode`. Every test below asserts on `response_code`, and
the negative cases additionally assert `http_status == 200` to pin that quirk in
place so a future change to it cannot pass silently.
"""
import uuid

import pytest

from utils.data_loader import load_json

# Exact message strings returned by the live API (verified, not paraphrased).
METHOD_NOT_SUPPORTED = "This request method is not supported."
SEARCH_PARAM_MISSING = "Bad request, search_product parameter is missing in POST request."
LOGIN_PARAM_MISSING = "Bad request, email or password parameter is missing in POST request."
USER_NOT_FOUND = "User not found!"
USER_EXISTS = "User exists!"
USER_CREATED = "User created!"
ACCOUNT_DELETED = "Account deleted!"
USER_UPDATED = "User updated!"

SEARCH_CASES = load_json("api_search_data.json")

pytestmark = pytest.mark.api


# --- API 1: GET productsList ------------------------------------------------
def test_api_01_get_all_products_list(api):
    """API 1 — GET productsList returns the full product catalogue."""
    resp = api.get_all_products()

    assert resp.http_status == 200
    assert resp.response_code == 200
    products = resp.get("products")
    assert isinstance(products, list) and products, "Expected a non-empty products list"
    for key in ("id", "name", "price", "brand", "category"):
        assert key in products[0], f"Product is missing {key!r}: {products[0]}"


# --- API 2: POST productsList (unsupported) ---------------------------------
def test_api_02_post_to_all_products_list_not_supported(api):
    """API 2 — POST productsList is not supported (405)."""
    resp = api.post_all_products()

    assert resp.http_status == 200  # the quirk: real code lives in the body
    assert resp.response_code == 405
    assert resp.message == METHOD_NOT_SUPPORTED


# --- API 3: GET brandsList --------------------------------------------------
def test_api_03_get_all_brands_list(api):
    """API 3 — GET brandsList returns all brands."""
    resp = api.get_all_brands()

    assert resp.http_status == 200
    assert resp.response_code == 200
    brands = resp.get("brands")
    assert isinstance(brands, list) and brands, "Expected a non-empty brands list"
    for key in ("id", "brand"):
        assert key in brands[0], f"Brand is missing {key!r}: {brands[0]}"


# --- API 4: PUT brandsList (unsupported) ------------------------------------
def test_api_04_put_to_all_brands_list_not_supported(api):
    """API 4 — PUT brandsList is not supported (405)."""
    resp = api.put_all_brands()

    assert resp.http_status == 200
    assert resp.response_code == 405
    assert resp.message == METHOD_NOT_SUPPORTED


# --- API 5: POST searchProduct (data-driven) --------------------------------
@pytest.mark.parametrize("data", SEARCH_CASES, ids=[c["term"] for c in SEARCH_CASES])
def test_api_05_search_product(api, data):
    """API 5 — POST searchProduct returns products matching the search term."""
    resp = api.search_product(data["term"])

    assert resp.http_status == 200
    assert resp.response_code == 200
    products = resp.get("products")
    assert isinstance(products, list) and products, (
        f"No products returned for search term {data['term']!r}"
    )
    names = " ".join(p["name"] for p in products).lower()
    assert data["expected_substring"].lower() in names, (
        f"None of the {len(products)} results mention "
        f"{data['expected_substring']!r}. Results: {names[:200]}"
    )


# --- API 6: POST searchProduct without search_product -----------------------
def test_api_06_search_product_without_param(api):
    """API 6 — POST searchProduct without the `search_product` field (400)."""
    resp = api.search_product_without_param()

    assert resp.http_status == 200
    assert resp.response_code == 400
    assert resp.message == SEARCH_PARAM_MISSING


# --- API 7: POST verifyLogin with valid details -----------------------------
def test_api_07_verify_login_valid(api, api_account):
    """API 7 — POST verifyLogin with valid credentials returns 'User exists!'."""
    resp = api.verify_login(api_account["email"], api_account["password"])

    assert resp.http_status == 200
    assert resp.response_code == 200
    assert resp.message == USER_EXISTS


# --- API 8: POST verifyLogin without email ----------------------------------
def test_api_08_verify_login_without_email(api):
    """API 8 — POST verifyLogin without the `email` field (400)."""
    resp = api.verify_login_without_email(password="S3cure!pass")

    assert resp.http_status == 200
    assert resp.response_code == 400
    assert resp.message == LOGIN_PARAM_MISSING


# --- API 9: DELETE verifyLogin (unsupported) --------------------------------
def test_api_09_verify_login_delete_not_supported(api):
    """API 9 — DELETE verifyLogin is not supported (405)."""
    resp = api.verify_login_via_delete()

    assert resp.http_status == 200
    assert resp.response_code == 405
    assert resp.message == METHOD_NOT_SUPPORTED


# --- API 10: POST verifyLogin with invalid details --------------------------
def test_api_10_verify_login_invalid(api):
    """API 10 — POST verifyLogin with unknown credentials returns 'User not found!'."""
    unknown_email = f"no.such.user.{uuid.uuid4().hex}@example.com"
    resp = api.verify_login(unknown_email, "definitely-wrong")

    assert resp.http_status == 200
    assert resp.response_code == 404
    assert resp.message == USER_NOT_FOUND


# --- API 11: POST createAccount ---------------------------------------------
def test_api_11_create_account(api, disposable_api_user):
    """API 11 — POST createAccount registers a new user (201, 'User created!').

    Confirms the account is real afterwards via verifyLogin; teardown deletes it.
    """
    resp = api.create_account(disposable_api_user)

    assert resp.response_code == 201
    assert resp.message == USER_CREATED

    verify = api.verify_login(disposable_api_user["email"], disposable_api_user["password"])
    assert verify.response_code == 200, "Created account does not verify as existing"


# --- API 12: DELETE deleteAccount -------------------------------------------
def test_api_12_delete_account(api, disposable_api_user):
    """API 12 — DELETE deleteAccount removes a user (200, 'Account deleted!')."""
    created = api.create_account(disposable_api_user)
    assert created.response_code == 201, "Precondition failed: account not created"

    resp = api.delete_account(disposable_api_user["email"], disposable_api_user["password"])

    assert resp.response_code == 200
    assert resp.message == ACCOUNT_DELETED

    gone = api.verify_login(disposable_api_user["email"], disposable_api_user["password"])
    assert gone.response_code == 404, "Account still verifies after deletion"


# --- API 13: PUT updateAccount ----------------------------------------------
def test_api_13_update_account(api, api_account):
    """API 13 — PUT updateAccount changes account fields (200, 'User updated!').

    Cross-checks the change against API 14 (getUserDetailByEmail).
    """
    updated = dict(api_account)
    updated["name"] = "QA Bot Updated"
    updated["city"] = "Seattle"

    resp = api.update_account(updated)

    assert resp.http_status == 200
    assert resp.response_code == 200
    assert resp.message == USER_UPDATED

    detail = api.get_user_detail_by_email(api_account["email"]).get("user")
    assert detail["name"] == "QA Bot Updated", "Updated name did not persist"
    assert detail["city"] == "Seattle", "Updated city did not persist"


# --- API 14: GET getUserDetailByEmail ---------------------------------------
def test_api_14_get_user_detail_by_email(api, api_account):
    """API 14 — GET getUserDetailByEmail returns the user's account detail."""
    resp = api.get_user_detail_by_email(api_account["email"])

    assert resp.http_status == 200
    assert resp.response_code == 200
    user = resp.get("user")
    assert isinstance(user, dict) and user, "Expected a populated `user` object"
    assert user["email"] == api_account["email"]
    assert user["name"] == api_account["name"]
    for key in ("id", "name", "email", "first_name", "last_name", "country"):
        assert key in user, f"User detail is missing {key!r}: {user}"
