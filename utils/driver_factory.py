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
    # 'eager' = continue at DOMContentLoaded instead of waiting for every ad
    # iframe to finish loading. The AUT is ad-heavy and slow third-party frames
    # otherwise stall navigation until the page-load timeout; all real
    # synchronisation is done via explicit waits anyway.
    opts.page_load_strategy = "eager"
    if Config.HEADLESS:
        opts.add_argument("--headless=new")
    width, height = Config.WINDOW_SIZE.split(",")
    opts.add_argument(f"--window-size={width},{height}")
    # Stability flags — required on CI containers, harmless locally.
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-notifications")
    # Anti-bot-detection: suppress the automation flags Cloudflare fingerprints.
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--lang=en-US,en;q=0.9")
    # Headless Chrome injects "HeadlessChrome" into the UA — replace it with a
    # normal desktop UA so Cloudflare's TLS/UA check sees a real browser.
    opts.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    )
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    # The AUT monetises with Google vignette ads that overlay the whole page,
    # intercepting clicks and freezing scroll. Null-route the ad domains at the
    # DNS level so the interstitials can never load.
    ad_hosts = [
        "pagead2.googlesyndication.com",
        "googleads.g.doubleclick.net",
        "securepubads.g.doubleclick.net",
        "tpc.googlesyndication.com",
        "www.googletagservices.com",
        "adservice.google.com",
        "ep1.adtrafficquality.google",
        "ep2.adtrafficquality.google",
        "fundingchoicesmessages.google.com",
    ]
    rules = ", ".join(f"MAP {host} 127.0.0.1" for host in ad_hosts)
    opts.add_argument(f"--host-resolver-rules={rules}")
    return opts


def _firefox_options() -> FirefoxOptions:
    opts = FirefoxOptions()
    opts.page_load_strategy = "eager"
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
        # Mask navigator.webdriver before any page script runs so Cloudflare's
        # JS challenge cannot detect the automation flag via the property getter.
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"},
        )
    elif browser == "firefox":
        driver = webdriver.Firefox(options=_firefox_options())
    else:
        raise ValueError(f"Unsupported BROWSER '{browser}'. Use 'chrome' or 'firefox'.")

    driver.set_page_load_timeout(Config.PAGE_LOAD_TIMEOUT)
    # No implicit wait is set on purpose — all synchronisation is explicit.
    return driver
