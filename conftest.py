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
