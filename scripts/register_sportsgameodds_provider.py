#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

provider = {
    "name": "sportsgameodds",
    "kind": ["events", "odds", "live"],
    "priority": 1,
    "status": "validated",
    "supports": {
        "sports": True,
        "leagues": True,
        "events_by_league": True,
        "events_by_event_id": True,
        "bookmaker_filter": True,
        "pagination": True,
        "live": True,
        "player_props": "pending_test"
    },
    "notes": [
        "Validado con /sports",
        "Validado con /leagues",
        "Validado con /v2/events?leagueID=NBA&oddsAvailable=true",
        "Tier actual requiere leagueID o eventID"
    ]
}

p = Path("cachediario/providerregistry.json")
p.parent.mkdir(parents=True, exist_ok=True)

if p.exists():
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        data = {}
else:
    data = {}

data["sportsgameodds"] = provider
p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("OK", p)
