"""Central configuration. All values are env-driven with sane defaults.

Nothing in the test/page layer should hardcode a URL, browser, or timeout.
Override anything via environment variables or a local .env file
(see .env.example). CI sets these as workflow env vars.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load a local .env if present.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def _as_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


class Config:
    # Target application under test
    BASE_URL: str = os.getenv("BASE_URL", "https://automationexercise.com")

    # Browser selection: "chrome" or "firefox"
    BROWSER: str = os.getenv("BROWSER", "chrome").lower()
    HEADLESS: bool = _as_bool(os.getenv("HEADLESS", "false"))
    WINDOW_SIZE: str = os.getenv("WINDOW_SIZE", "1920,1080")

    # Waits (seconds). Explicit waits only — there is no implicit wait set.
    EXPLICIT_TIMEOUT: int = int(os.getenv("EXPLICIT_TIMEOUT", "15"))
    PAGE_LOAD_TIMEOUT: int = int(os.getenv("PAGE_LOAD_TIMEOUT", "30"))

    # Output locations
    LOG_DIR: Path = PROJECT_ROOT / os.getenv("LOG_DIR", "logs")
    SCREENSHOT_DIR: Path = PROJECT_ROOT / os.getenv("SCREENSHOT_DIR", "screenshots")
    REPORT_DIR: Path = PROJECT_ROOT / os.getenv("REPORT_DIR", "reports")
    DATA_DIR: Path = PROJECT_ROOT / "data"

    @classmethod
    def ensure_dirs(cls) -> None:
        for d in (cls.LOG_DIR, cls.SCREENSHOT_DIR, cls.REPORT_DIR):
            d.mkdir(parents=True, exist_ok=True)

    @classmethod
    def as_dict(cls) -> dict:
        return {
            "BASE_URL": cls.BASE_URL,
            "BROWSER": cls.BROWSER,
            "HEADLESS": cls.HEADLESS,
            "WINDOW_SIZE": cls.WINDOW_SIZE,
            "EXPLICIT_TIMEOUT": cls.EXPLICIT_TIMEOUT,
            "PAGE_LOAD_TIMEOUT": cls.PAGE_LOAD_TIMEOUT,
        }
