from __future__ import annotations

from typing import Any
import os
import time
import requests

BASE_URL = "https://odds-api1.p.rapidapi.com"
TIMEOUT = 25
SPORT_IDS = {"tenis": 12, "futbol": 10, "basket": 11}

_session = requests.Session()
_cache: dict[str, list[dict[str, Any]]] = {}


def _headers() -> dict[str, str]:
    return {
        "x-rapidapi-key": os.environ.get("RAPIDAPI_KEY", ""),
        "x-rapidapi-host": "odds-api1.p.rapidapi.com",
        "Content-Type": "application/json",
    }


def _request(url: str, params: dict[str, Any], retries: int = 5):
    delay = 1.0
    last_exc: Exception | None = None

    for _ in range(retries):
        try:
            r = _session.get(url, headers=_headers(), params=params, timeout=TIMEOUT)
            if r.status_code == 429:
                ra = r.headers.get("Retry-After")
                if ra:
                    try:
                        time.sleep(float(ra))
                    except ValueError:
                        time.sleep(delay)
                else:
                    time.sleep(delay)
                delay = min(delay * 2, 60)
                continue
            r.raise_for_status()
            return r.json(), r
        except Exception as exc:
            last_exc = exc
            time.sleep(delay)
            delay = min(delay * 2, 60)

    if last_exc:
        raise last_exc
    return None, None


def _fetch_today_fixtures(sport_id: int) -> list[dict[str, Any]]:
    data, _ = _request(f"{BASE_URL}/fixtures/today", {"sportId": sport_id})
    return data if isinstance(data, list) else []


def get_today_fixtures(sport: str, limit: int = 20, min_pause: float = 0.0) -> list[dict[str, Any]]:
    sport = sport.lower().strip()
    if sport in _cache:
        return _cache[sport][:limit]

    sport_id = SPORT_IDS.get(sport)
    if not sport_id:
        return []

    today = _fetch_today_fixtures(sport_id)
    rows: list[dict[str, Any]] = []

    for item in today:
        if len(rows) >= limit:
            break

        rows.append({
            "fixture_id": item.get("fixtureId"),
            "sport": (item.get("sport") or {}).get("sportName"),
            "league": (item.get("tournament") or {}).get("tournamentName"),
            "home": (item.get("participants") or {}).get("participant1Name"),
            "away": (item.get("participants") or {}).get("participant2Name"),
            "status": (item.get("status") or {}).get("statusName"),
            "live": (item.get("status") or {}).get("live"),
        })

        if min_pause > 0:
            time.sleep(min_pause)

    _cache[sport] = rows
    return rows
