#!/usr/bin/env python3
from __future__ import annotations
import json
import requests
from core.config import Config

key = Config.SPORTSGAME_ODDS_KEY
headers = {"x-api-key": key, "Accept": "application/json"}

tests = [
    "https://api.sportsgameodds.com/sports",
    "https://api.sportsgameodds.com/leagues",
    "https://api.sportsgameodds.com/bookmakers",
]

for url in tests:
    r = requests.get(url, headers=headers, timeout=10)
    print(f"{r.status_code} | {url}")
    try:
        data = r.json()
    except Exception:
        data = {"raw": r.text[:500]}
    if r.status_code == 200:
        print(json.dumps(data, ensure_ascii=False, indent=2)[:800] + "...")
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2)[:500] + "...")
