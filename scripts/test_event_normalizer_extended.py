#!/usr/bin/env python3
from __future__ import annotations
from sharedprovidersrouter import get_events_for_league
from sharedeventnormalizer import normalize_sgo_event

for league in ["NBA", "MLS"]:
    res = get_events_for_league(league, limit=1)
    events = res.get("result", {}).get("data", {}).get("data", []) if res.get("ok") else []
    print("=" * 80)
    print("LEAGUE:", league)
    for raw in events[:1]:
        norm = normalize_sgo_event(raw)
        print("EVENT:", norm["event_id"])
        print("SPORT:", norm["sport_id"])
        print("HOME:", norm["home_team"]["name"])
        print("AWAY:", norm["away_team"]["name"])
        print("LIVE:", norm["live"])
        print("STATUS:", norm["display_status"])
        print("VENUE:", norm["venue"])
        print("ODDS_AVAILABLE:", norm["odds_available"])
        print("ODDS_PRESENT:", norm["odds_present"])
        print("BOOKMAKER_LINKS_COUNT:", len(norm["bookmaker_links"]))
        print("RAW_ODDS_TYPE:", type(norm["raw_odds"]).__name__)
