"""Pytest fixtures and hooks.

- `driver` is function-scoped: each test gets a clean browser session so state
  (cookies, logged-in user) never leaks between tests. For a UI suite this
  isolation is worth the per-test launch cost; a session-scoped driver is
  faster but couples tests together, which is a worse default.
- `pytest_runtest_makereport` captures a screenshot on failure and embeds it
  in the pytest-html report.
"""
import datetime

import pytest

from config.config import Config
from utils.driver_factory import create_driver
from utils.logger import get_logger

log = get_logger("conftest")


@pytest.fixture(scope="session", autouse=True)
def _prepare_environment():
    Config.ensure_dirs()
    log.info("Test session config: %s", Config.as_dict())
    yield


@pytest.fixture(scope="function")
def driver():
    drv = create_driver()
    yield drv
    log.info("Quitting browser")
    drv.quit()


@pytest.fixture(scope="function")
def registered_user(driver):
    """Register a fresh account via the UI, log out, and hand the credentials
    to the test. Teardown deletes the account best-effort — several test cases
    (e.g. 'Login User', 'Place Order') delete it themselves as a final step,
    in which case cleanup is a no-op.
    """
    from pages.home_page import HomePage
    from pages.login_page import LoginPage
    from tests.flows import delete_account, register_user
    from utils.user_factory import new_user

    user = new_user()
    home = register_user(driver, user)
    home.logout()
    yield user

    try:
        home = HomePage(driver)
        if not home.is_logged_in():
            login = LoginPage(driver).load()
            login.login(user["email"], user["password"])
        if home.is_logged_in():
            delete_account(driver)
    except Exception as exc:  # pragma: no cover - defensive cleanup
        log.warning("Could not clean up account %s: %s", user["email"], exc)


@pytest.fixture(scope="function")
def api():
    """A ready-to-use AutomationExercise API client with a pooled session.

    Browserless — API tests never request the `driver` fixture, so they run fast
    and stay green even when the UI target is flaky behind Cloudflare.
    """
    from api import AutomationExerciseApiClient

    client = AutomationExerciseApiClient()
    yield client
    client.close()


@pytest.fixture(scope="function")
def api_account(api):
    """Create a fresh account via the API, hand its payload to the test, and
    delete it on teardown. Cleanup is best-effort and idempotent: tests that
    delete the account themselves (e.g. the deleteAccount case) leave teardown a
    no-op, since deleting a missing account simply returns 404.
    """
    from utils.user_factory import new_api_user

    user = new_api_user()
    created = api.create_account(user)
    assert created.response_code == 201, (
        f"Fixture could not create an account: {created!r}"
    )
    yield user

    try:
        resp = api.delete_account(user["email"], user["password"])
        if resp.response_code not in (200, 404):
            log.warning("Unexpected cleanup response for %s: %s", user["email"], resp)
    except Exception as exc:  # pragma: no cover - defensive cleanup
        log.warning("Could not clean up API account %s: %s", user["email"], exc)


@pytest.fixture(scope="function")
def disposable_api_user(api):
    """Hand a test a fresh, *uncreated* API registration payload and guarantee
    the account is gone afterwards. Lets the create/delete tests own the
    create/delete calls themselves while teardown still cleans up an account the
    test left behind (deleting a missing account is a harmless 404).
    """
    from utils.user_factory import new_api_user

    user = new_api_user()
    yield user

    try:
        api.delete_account(user["email"], user["password"])
    except Exception as exc:  # pragma: no cover - defensive cleanup
        log.warning("Could not clean up API account %s: %s", user["email"], exc)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach a screenshot to the HTML report whenever a test's call phase fails."""
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    drv = item.funcargs.get("driver")
    if drv is None:
        return

    Config.ensure_dirs()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = item.name.replace("/", "_").replace("[", "_").replace("]", "")
    screenshot_path = Config.SCREENSHOT_DIR / f"{safe_name}_{timestamp}.png"

    try:
        drv.save_screenshot(str(screenshot_path))
        log.error("Test failed — screenshot saved: %s", screenshot_path)
    except Exception as exc:  # pragma: no cover - defensive
        log.error("Could not capture screenshot: %s", exc)
        return

    # Embed into pytest-html if the plugin is active (API differs across versions).
    html_plugin = item.config.pluginmanager.getplugin("html")
    if html_plugin is not None:
        extras = getattr(report, "extras", getattr(report, "extra", []))
        extras.append(html_plugin.extras.image(str(screenshot_path)))
        if hasattr(report, "extras"):
            report.extras = extras
        else:  # pytest-html < 4
            report.extra = extras
