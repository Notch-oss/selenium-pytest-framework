"""Tiny helpers to load external test data (JSON) for @parametrize."""
import json

from config.config import Config


def load_json(filename: str) -> list:
    path = Config.DATA_DIR / filename
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)
