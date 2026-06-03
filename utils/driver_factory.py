"""WebDriver construction. Browser, headless mode, and window size come from
Config (env-driven). Selenium 4.6+ ships Selenium Manager, so we do NOT need
webdriver-manager or a manually downloaded driver binary on PATH.
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from config.config import Config
from utils.logger import get_logger

log = get_logger(__name__)


def _chrome_options() -> ChromeOptions:
    opts = ChromeOptions()
    if Config.HEADLESS:
        opts.add_argument("--headless=new")
    width, height = Config.WINDOW_SIZE.split(",")
    opts.add_argument(f"--window-size={width},{height}")
    # Stability flags — required on CI containers, harmless locally.
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-notifications")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    return opts


def _firefox_options() -> FirefoxOptions:
    opts = FirefoxOptions()
    if Config.HEADLESS:
        opts.add_argument("-headless")
    width, height = Config.WINDOW_SIZE.split(",")
    opts.add_argument(f"--width={width}")
    opts.add_argument(f"--height={height}")
    return opts


def create_driver() -> webdriver.Remote:
    browser = Config.BROWSER
    log.info("Launching browser=%s headless=%s", browser, Config.HEADLESS)

    if browser == "chrome":
        driver = webdriver.Chrome(options=_chrome_options())
    elif browser == "firefox":
        driver = webdriver.Firefox(options=_firefox_options())
    else:
        raise ValueError(f"Unsupported BROWSER '{browser}'. Use 'chrome' or 'firefox'.")

    driver.set_page_load_timeout(Config.PAGE_LOAD_TIMEOUT)
    # No implicit wait is set on purpose — all synchronisation is explicit.
    return driver
