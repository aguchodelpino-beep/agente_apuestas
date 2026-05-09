from __future__ import annotations

import os
from itertools import cycle
from typing import Any
import requests

BASE_URL = "https://api.the-odds-api.com/v4"

ODDS_KEYS = [k.strip() for k in os.getenv("ODDS_API_KEYS", "").split(",") if k.strip()]
KEY_ROTATOR = cycle(ODDS_KEYS) if ODDS_KEYS else None


def get_next_key() -> str:
    if KEY_ROTATOR is None:
        raise RuntimeError("ODDS_API_KEYS no configurado en entorno")
    return next(KEY_ROTATOR)


def fetch_fixtures(sport_key: str, regions: str = "eu", markets: str = "h2h", timeout: int = 20) -> list[dict[str, Any]]:
    api_key = get_next_key()
    url = f"{BASE_URL}/sports/{sport_key}/odds"
    params = {
        "apiKey": api_key,
        "regions": regions,
        "markets": markets,
        "oddsFormat": "decimal",
    }
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    return data if isinstance(data, list) else []


def test_rotator() -> str:
    if not ODDS_KEYS:
        return "ODDS_API_KEYS vacío"
    checked = 0
    for _ in range(min(3, len(ODDS_KEYS))):
        key = get_next_key()
        checked += 1
        try:
            r = requests.get(
                f"{BASE_URL}/sports",
                params={"apiKey": key},
                timeout=10,
            )
            if r.status_code == 200:
                return f"OK key #{checked} {key[:8]}..."
        except Exception:
            pass
    return "sin key funcional en primeras 3"
