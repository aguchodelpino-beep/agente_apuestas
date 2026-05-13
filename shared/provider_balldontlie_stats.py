from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(".env").resolve(), override=False)

BASE = "https://api.balldontlie.io"
API_KEY = (os.getenv("BALLDONTLIE_API_KEY") or "").strip()
_LAST_CALL_TS = 0.0
_MIN_INTERVAL = 1.1


def _headers() -> dict[str, str]:
    if not API_KEY:
        raise RuntimeError("Falta BALLDONTLIE_API_KEY en .env")
    return {"Authorization": API_KEY}


def _get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    global _LAST_CALL_TS
    now = time.monotonic()
    wait = _MIN_INTERVAL - (now - _LAST_CALL_TS)
    if wait > 0:
        time.sleep(wait)
    url = f"{BASE}{path}"
    r = requests.get(url, headers=_headers(), params=params or {}, timeout=30)
    _LAST_CALL_TS = time.monotonic()
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, dict):
        raise RuntimeError(f"Respuesta no esperada en {path}")
    return data


def nba_get_teams(page: int = 1, per_page: int = 30) -> dict[str, Any]:
    return _get("/v1/teams", {"page": page, "per_page": per_page})


def nba_get_games_by_date(date_str: str, per_page: int = 25) -> dict[str, Any]:
    return _get("/nba/v1/games", {"dates[]": date_str, "per_page": per_page})

if __name__ == "__main__":
    print("SCRIPT OK")
