#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import requests

API_KEY = os.environ.get("RAPIDAPI_KEY", os.getenv("RAPIDAPIKEY", "TEST"))
BASE_URL = "https://odds-api1.p.rapidapi.com"
TIMEOUT = 25
SPORTS = {"tenis": 12, "futbol": 10, "basket": 11}
BOOKMAKERS = "pinnacle,stake,draftkings"

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)


def headers() -> dict[str, str]:
    return {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "odds-api1.p.rapidapi.com",
        "Content-Type": "application/json",
    }


def fetch_today_fixtures(sport_id: int) -> list[dict]:
    r = requests.get(
        f"{BASE_URL}/fixtures/today",
        headers=headers(),
        params={"sportId": sport_id},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    data = r.json()
    return data if isinstance(data, list) else []


def fetch_main_odds(fixture_id: str) -> list[dict]:
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
    summary = {}

    for sport_name, sport_id in SPORTS.items():
        today = fetch_today_fixtures(sport_id)
        picked = today[:10]
        results = []

        for item in picked:
            fixture_id = item.get("fixtureId")
            if not fixture_id:
                continue

            odds_items = fetch_main_odds(fixture_id)
            books = []
            if odds_items:
                first = odds_items[0]
                odds = first.get("odds") or {}
                books = sorted(list(odds.keys()))

            results.append({
                "fixture_id": fixture_id,
                "home": (item.get("participants") or {}).get("participant1Name"),
                "away": (item.get("participants") or {}).get("participant2Name"),
                "league": (item.get("tournament") or {}).get("tournamentName"),
                "books": books,
            })

        out_path = RAW_DIR / f"odds_api1_{sport_name}_main_odds_check.json"
        out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

        summary[sport_name] = {
            "checked": len(results),
            "with_books": sum(1 for x in results if x["books"]),
            "sample": results[:3],
        }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
