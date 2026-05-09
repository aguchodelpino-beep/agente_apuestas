#!/usr/bin/env python3
from __future__ import annotations
from sharedprovidersrouter import get_events_for_league
from sharedeventnormalizer import normalize_sgo_event
from sharedoddsnormalizer import normalize_sgo_odds

res = get_events_for_league("NBA", limit=1)
events = res.get("result", {}).get("data", {}).get("data", []) if res.get("ok") else []

for raw in events:
    norm_event = normalize_sgo_event(raw)
    raw_odds = norm_event["raw_odds"]
    odds = normalize_sgo_odds(raw_odds)
    
    print("=" * 80)
    print("EVENT:", norm_event["event_id"])
    print("HOME:", norm_event["home_team"]["name"])
    print("RAW_ODDS_KEYS:", list(raw_odds.keys())[:10] if isinstance(raw_odds, dict) else "no odds")
    print("NORMALIZED_ODDS_COUNT:", len(odds))
    
    if odds:
        first = odds[0]
        print("EJEMPLO:")
        print("  Bookmaker:", first["bookmaker_id"])
        print("  Market:", first["market"])
        print("  Side:", first["side"])
        print("  Decimal:", first["decimal_odds"])
        print("  Fair:", first["fair_odds"])
        break
