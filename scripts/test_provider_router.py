#!/usr/bin/env python3
from __future__ import annotations
import json
from sharedprovidersrouter import get_events_for_league

for league in ["NBA", "MLS", "MLB"]:
    res = get_events_for_league(league, limit=2)
    print("=" * 80)
    print("LEAGUE:", league)
    print("OK:", res["ok"])
    print("PROVIDER:", res["provider"])
    if res["ok"]:
        payload = res["result"]["data"]
        print("TOP_KEYS:", list(payload.keys())[:10] if isinstance(payload, dict) else type(payload))
        print("COUNT:", len(payload.get("data", [])) if isinstance(payload, dict) else 0)
        if isinstance(payload, dict) and payload.get("data"):
            ev = payload["data"][0]
            print("EVENT_ID:", ev.get("eventID"))
            print("SPORT:", ev.get("sportID"))
            print("LEAGUE_ID:", ev.get("leagueID"))
            print("LIVE:", ev.get("status", {}).get("live"))
    else:
        print(json.dumps(res["error"], ensure_ascii=False, indent=2)[:1000])
