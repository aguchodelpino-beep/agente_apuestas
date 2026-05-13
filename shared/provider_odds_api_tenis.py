from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.the-odds-api.com/v4/sports"
OUT_DIR = Path("data/raw/tenis")
DEFAULT_KEYS = [
    "tennis_atp_italian_open",
    "tennis_atp_french_open",
    "tennis_atp_madrid_open",
    "tennis_atp_miami_open",
    "tennis_atp_monte_carlo_masters",
]


def _api_key() -> str:
    key = os.getenv("ODDS_API_KEY") or os.getenv("SPORTS_API_KEY") or ""
    if not key.strip():
        raise RuntimeError("Falta ODDS_API_KEY o SPORTS_API_KEY en .env")
    return key.strip()


def _today_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _request_json(url: str, params: dict[str, Any]) -> Any:
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def _normalize_event(sport_key: str, row: dict[str, Any]) -> dict[str, Any]:
    home = row.get("home_team") or row.get("home") or "TBD"
    away_teams = row.get("away_team")
    if not away_teams:
        teams = row.get("teams", [])
        if isinstance(teams, list) and len(teams) >= 2:
            away_teams = next((x for x in teams if x != home), teams[1])
    away = away_teams or "TBD"

    return {
        "fixture_id": row.get("id") or f"{sport_key}-{row.get('commence_time','na')}-{home}-{away}",
        "sport": "tenis",
        "league": sport_key,
        "home": home,
        "away": away,
        "start_time": row.get("commence_time"),
        "status": "scheduled",
        "source": "odds_api",
        "markets": row.get("bookmakers", []),
        "raw": row,
    }


def fetch_tennis_odds(sport_keys: list[str] | None = None) -> list[dict[str, Any]]:
    keys = sport_keys or DEFAULT_KEYS
    api_key = _api_key()
    rows: list[dict[str, Any]] = []

    for sport_key in keys:
        url = f"{BASE_URL}/{sport_key}/odds"
        params = {
            "apiKey": api_key,
            "regions": "eu",
            "markets": "h2h",
            "oddsFormat": "decimal",
            "dateFormat": "iso",
        }
        try:
            data = _request_json(url, params)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        rows.append(_normalize_event(sport_key, item))
        except Exception:
            continue

    return rows


def save_daily_tennis_cache(sport_keys: list[str] | None = None) -> Path:
    rows = fetch_tennis_odds(sport_keys=sport_keys)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    payload = {
        "sport": "tenis",
        "date": _today_utc(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "odds_api",
        "records_count": len(rows),
        "payload_hash": hashlib.sha256(
            json.dumps(rows, ensure_ascii=False, sort_keys=True).encode("utf-8")
        ).hexdigest(),
        "payload": rows,
    }

    out = OUT_DIR / f"{payload['date']}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


if __name__ == "__main__":
    path = save_daily_tennis_cache()
    print(path)

if __name__ == "__main__":
    print("SCRIPT OK")
