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
    print("RAW_ODD_IDS:", list(raw_odds.keys())[:5] if isinstance(raw_odds, dict) else [])
    print("NORMALIZED_ODDS_COUNT:", len(odds))

    if odds:
        first = odds[0]
        print("EJEMPLO:")
        print("  odd_id:", first["odd_id"])
        print("  bookmaker_id:", first["bookmaker_id"])
        print("  stat_id:", first["stat_id"])
        print("  stat_entity_id:", first["stat_entity_id"])
        print("  period_id:", first["period_id"])
        print("  bet_type_id:", first["bet_type_id"])
        print("  side_id:", first["side_id"])
        print("  odds:", first["odds"])
        print("  available:", first["available"])
        print("  fair_odds:", first["fair_odds"])
        print("  book_odds:", first["book_odds"])
        break
