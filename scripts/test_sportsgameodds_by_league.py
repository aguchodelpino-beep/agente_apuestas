#!/usr/bin/env python3
from __future__ import annotations
import json
import requests
from core.config import Config

key = Config.SPORTSGAME_ODDS_KEY
headers = {"x-api-key": key, "Accept": "application/json"}

tests = [
    ("nba", "NBA"),
    ("mls", "MLS"),
    ("mlb", "MLB"),
]

for name, league_id in tests:
    url = "https://api.sportsgameodds.com/v2/events"
    params = {
        "leagueID": league_id,
        "oddsAvailable": "true",
        "limit": 2,
    }
    r = requests.get(url, headers=headers, params=params, timeout=15)
    print("=" * 80)
    print(name, r.status_code, r.url)
    try:
        data = r.json()
    except Exception:
        data = {"raw": r.text[:1200]}

    if isinstance(data, dict):
        print("keys:", list(data.keys())[:20])
        if "data" in data and isinstance(data["data"], list):
            print("count:", len(data["data"]))
            if data["data"]:
                print(json.dumps(data["data"][0], ensure_ascii=False, indent=2)[:1800])
        else:
            print(json.dumps(data, ensure_ascii=False, indent=2)[:1200])
    else:
        print(str(data)[:1200])
