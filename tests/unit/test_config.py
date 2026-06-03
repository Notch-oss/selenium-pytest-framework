"""Browserless unit tests for the config layer.

These run without a WebDriver, so CI verifies wiring (env overrides, bool
parsing) even when the target site is flaky or unreachable.
"""
import importlib

import config.config as config_module


def _reload_config():
    return importlib.reload(config_module).Config


def test_defaults_present():
    cfg = _reload_config()
    assert cfg.BASE_URL.startswith("http")
    assert cfg.BROWSER in {"chrome", "firefox"}
    assert isinstance(cfg.EXPLICIT_TIMEOUT, int)


def test_env_override(monkeypatch):
    monkeypatch.setenv("BASE_URL", "https://example.org")
    monkeypatch.setenv("BROWSER", "firefox")
    monkeypatch.setenv("HEADLESS", "true")
    monkeypatch.setenv("EXPLICIT_TIMEOUT", "42")
    cfg = _reload_config()
    assert cfg.BASE_URL == "https://example.org"
    assert cfg.BROWSER == "firefox"
    assert cfg.HEADLESS is True
    assert cfg.EXPLICIT_TIMEOUT == 42


def test_bool_parsing(monkeypatch):
    for raw, expected in [("1", True), ("YES", True), ("on", True),
                          ("0", False), ("false", False), ("no", False)]:
        monkeypatch.setenv("HEADLESS", raw)
        cfg = _reload_config()
        assert cfg.HEADLESS is expected, f"{raw!r} should parse to {expected}"
