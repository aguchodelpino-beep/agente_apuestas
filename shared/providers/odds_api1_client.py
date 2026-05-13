from __future__ import annotations

import os
from typing import Any
import requests

BASE_URL = "https://odds-api1.p.rapidapi.com"


def _headers() -> dict[str, str]:
    api_key = os.environ.get("RAPIDAPI_KEY", "")
    return {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "odds-api1.p.rapidapi.com",
        "Content-Type": "application/json",
    }


def fetch_fixtures_by_sport(sport_id: int, timeout: int = 25) -> list[dict[str, Any]]:
    url = f"{BASE_URL}/fixtures/today"
    params = {"sportId": sport_id}
    r = requests.get(url, headers=_headers(), params=params, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    return data if isinstance(data, list) else []

if __name__ == "__main__":
    print("SCRIPT OK")
