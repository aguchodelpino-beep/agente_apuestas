from __future__ import annotations

import json
import os
from datetime import datetime, date
from pathlib import Path
from typing import Any
import requests

BASE_URL = "https://odds-api1.p.rapidapi.com"
TIMEOUT = 25
SPORT_IDS = {"tenis": 12, "futbol": 10, "basket": 11}

RAW_DIR = Path("data/raw")
META_DIR = Path("data/meta")
RAW_DIR.mkdir(parents=True, exist_ok=True)
META_DIR.mkdir(parents=True, exist_ok=True)

session = requests.Session()


def _headers() -> dict[str, str]:
    return {
        "x-rapidapi-key": os.environ.get("RAPIDAPI_KEY", ""),
        "x-rapidapi-host": "odds-api1.p.rapidapi.com",
        "Content-Type": "application/json",
    }


def _today_str() -> str:
    return date.today().isoformat()


def _sport_file(sport: str) -> Path:
    sport = sport.lower().strip()
    return RAW_DIR / sport / f"{_today_str()}.json"


def _fetch_today_fixtures(sport_id: int) -> list[dict[str, Any]]:
    r = session.get(
        f"{BASE_URL}/fixtures/today",
        headers=_headers(),
        params={"sportId": sport_id},
        timeout=TIMEOUT,
    )
    if r.status_code == 429:
        raise RuntimeError("rate_limited")
    r.raise_for_status()
    data = r.json()
    return data if isinstance(data, list) else []


def refresh_sport_cache(sport: str) -> list[dict[str, Any]]:
    sport = sport.lower().strip()
    sport_id = SPORT_IDS.get(sport)
    if not sport_id:
        return []

    items = _fetch_today_fixtures(sport_id)
    path = _sport_file(sport)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    return items


def load_sport_cache(sport: str) -> list[dict[str, Any]]:
    path = _sport_file(sport)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def get_sport_fixtures(sport: str, auto_refresh: bool = True) -> list[dict[str, Any]]:
    cached = load_sport_cache(sport)
    if cached:
        return cached

    if not auto_refresh:
        return []

    try:
        return refresh_sport_cache(sport)
    except Exception:
        return []


def get_fixture_rows(sport: str) -> list[dict[str, Any]]:
    items = get_sport_fixtures(sport)
    rows: list[dict[str, Any]] = []
    for item in items:
        rows.append({
            "fixture_id": item.get("fixtureId"),
            "sport": (item.get("sport") or {}).get("sportName"),
            "league": (item.get("tournament") or {}).get("tournamentName"),
            "home": (item.get("participants") or {}).get("participant1Name"),
            "away": (item.get("participants") or {}).get("participant2Name"),
            "status": (item.get("status") or {}).get("statusName"),
            "live": (item.get("status") or {}).get("live"),
        })
    return rows


def refresh_all() -> dict[str, int]:
    out: dict[str, int] = {}
    for sport in SPORT_IDS:
        try:
            out[sport] = len(refresh_sport_cache(sport))
        except Exception:
            out[sport] = 0
    return out
