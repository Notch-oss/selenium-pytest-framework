"""Product search scenarios — data-driven from data/search_data.json."""
import pytest

from pages.products_page import ProductsPage
from utils.data_loader import load_json

SEARCH_CASES = load_json("search_data.json")


@pytest.mark.regression
@pytest.mark.parametrize("data", SEARCH_CASES, ids=[c["term"] for c in SEARCH_CASES])
def test_search_returns_relevant_products(driver, data):
    products = ProductsPage(driver).load()
    products.dismiss_consent_if_present()
    products.search(data["term"])

    count = products.result_count()
    assert count > 0, f"No products returned for search term {data['term']!r}"

    names = " ".join(products.result_names()).lower()
    assert data["expected_substring"].lower() in names, (
        f"None of the {count} results mention {data['expected_substring']!r}. "
        f"Results: {names[:200]}"
    )
