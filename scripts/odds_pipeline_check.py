#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import requests

API_KEY = os.environ.get("RAPIDAPI_KEY", os.getenv("RAPIDAPIKEY", "TEST"))
BASE_URL = "https://odds-api1.p.rapidapi.com"
TIMEOUT = 25
SPORTS = {"tenis": 12, "futbol": 10, "basket": 11}
RAW_DIR = Path("data/raw")
LOG_DIR = Path("logs")
RAW_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class NormalizedFixture:
    fixture_id: str | None
    sport_id: int | None
    sport_name: str | None
    league_id: int | None
    league_name: str | None
    category_name: str | None
    home: str | None
    away: str | None
    live: bool | None
    status_id: int | None
    status_name: str | None
    participant1_abbr: str | None
    participant2_abbr: str | None
    odds_bookmakers: list[str]
    raw: dict[str, Any]

def headers() -> dict[str, str]:
    return {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "odds-api1.p.rapidapi.com",
        "Content-Type": "application/json",
    }

def fetch_fixtures_by_sport(sport_id: int) -> list[dict[str, Any]]:
    r = requests.get(f"{BASE_URL}/fixtures/today", headers=headers(), params={"sportId": sport_id}, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    return data if isinstance(data, list) else []

def normalize_fixture(item: dict[str, Any]) -> dict[str, Any]:
    sport = item.get("sport") or {}
    tournament = item.get("tournament") or {}
    participants = item.get("participants") or {}
    status = item.get("status") or {}
    odds = item.get("odds") or {}
    bookmakers = item.get("bookmakers") or {}
    odds_bookmakers = sorted(list(odds.keys())) or sorted(list(bookmakers.keys()))
    return asdict(NormalizedFixture(
        fixture_id=item.get("fixtureId"),
        sport_id=sport.get("sportId"),
        sport_name=sport.get("sportName"),
        league_id=tournament.get("tournamentId"),
        league_name=tournament.get("tournamentName"),
        category_name=tournament.get("categoryName"),
        home=participants.get("participant1Name"),
        away=participants.get("participant2Name"),
        live=status.get("live"),
        status_id=status.get("statusId"),
        status_name=status.get("statusName"),
        participant1_abbr=participants.get("participant1Abbr"),
        participant2_abbr=participants.get("participant2Abbr"),
        odds_bookmakers=odds_bookmakers,
        raw=item,
    ))

def save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def main() -> int:
    summary = {}
    for sport_name, sport_id in SPORTS.items():
        raw_items = fetch_fixtures_by_sport(sport_id)
        normalized = [normalize_fixture(x) for x in raw_items]
        live = [x for x in normalized if x.get("live") is True]
        save_json(RAW_DIR / f"odds_api1_{sport_name}_raw.json", raw_items)
        save_json(RAW_DIR / f"odds_api1_{sport_name}_normalized.json", normalized)
        summary[sport_name] = {
            "sport_id": sport_id,
            "total": len(normalized),
            "live": len(live),
            "first_fixture": normalized[0]["fixture_id"] if normalized else None,
            "first_title": f'{normalized[0]["home"]} vs {normalized[0]["away"]}' if normalized else None,
            "first_league": normalized[0]["league_name"] if normalized else None,
            "first_odds_bookmakers": normalized[0]["odds_bookmakers"] if normalized else [],
        }
    save_json(LOG_DIR / "odds_pipeline_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
