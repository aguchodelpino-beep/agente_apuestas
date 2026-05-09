#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
import requests

API_KEY = os.environ.get("RAPIDAPI_KEY", os.getenv("RAPIDAPIKEY", "TEST"))
BASE_URL = "https://odds-api1.p.rapidapi.com"
TIMEOUT = 25
SPORTS = {"tenis": 12, "futbol": 10, "basket": 11}
BOOKMAKERS = "pinnacle,stake,draftkings"

RAW_DIR = Path("data/raw")
LOG_DIR = Path("logs")
RAW_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

def headers() -> dict[str, str]:
    return {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "odds-api1.p.rapidapi.com",
        "Content-Type": "application/json",
    }

def fetch_today_fixtures(sport_id: int) -> list[dict[str, Any]]:
    r = requests.get(f"{BASE_URL}/fixtures/today", headers=headers(), params={"sportId": sport_id}, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    return data if isinstance(data, list) else []

def fetch_main_odds(fixture_id: str) -> list[dict[str, Any]]:
    r = requests.get(
        f"{BASE_URL}/fixtures/odds/main",
        headers=headers(),
        params={"fixtureIds": fixture_id, "bookmakers": BOOKMAKERS},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    data = r.json()
    return data if isinstance(data, list) else []

def main() -> int:
    summary: dict[str, Any] = {}
    for sport_name, sport_id in SPORTS.items():
        today = fetch_today_fixtures(sport_id)
        picked = today[:20]
        rows = []

        for item in picked:
            fixture_id = item.get("fixtureId")
            if not fixture_id:
                continue

            odds_items = fetch_main_odds(fixture_id)
            books: list[str] = []
            if odds_items:
                first = odds_items[0]
                odds = first.get("odds") or {}
                books = sorted(list(odds.keys()))

            rows.append({
                "fixture_id": fixture_id,
                "home": (item.get("participants") or {}).get("participant1Name"),
                "away": (item.get("participants") or {}).get("participant2Name"),
                "league": (item.get("tournament") or {}).get("tournamentName"),
                "status": (item.get("status") or {}).get("statusName"),
                "books": books,
            })

        usable = [x for x in rows if x["books"]]
        RAW_DIR.joinpath(f"odds_value_pipeline_{sport_name}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        summary[sport_name] = {"checked": len(rows), "usable": len(usable), "sample": usable[:5]}

    LOG_DIR.joinpath("odds_value_pipeline_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
