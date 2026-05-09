#!/usr/bin/env python3
import json
import requests
from core.config import Config

# Nombres reales que usa tu Config (por el error anterior sabemos que usa _ )
key = getattr(Config, 'SPORTSGAME_ODDS_KEY', None) or getattr(Config, 'SPORTSGAMEODDSKEY', None)
print(f"Key encontrada: {'✓' if key else '❌'}")

if key:
    headers = {"x-api-key": key, "Accept": "application/json"}
    for endpoint in ["sports", "leagues", "bookmakers"]:
        url = f"https://api.sportsgameodds.com/{endpoint}"
        r = requests.get(url, headers=headers, timeout=10)
        print(f"{r.status_code} | {url}")
        if r.status_code == 200:
            print(json.dumps(r.json(), indent=2)[:400] + "...\n")
        else:
            print(r.text[:200] + "\n")
