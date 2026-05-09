#!/usr/bin/env python3
from __future__ import annotations
from sharedprovidersrouter import get_events_for_league
from sharedeventnormalizer import normalize_sgo_event

res = get_events_for_league("NBA", limit=2)
events = res.get("result", {}).get("data", {}).get("data", []) if res.get("ok") else []

for raw in events[:2]:
    norm = normalize_sgo_event(raw)
    print("-" * 80)
    print("RAW SPORT:", raw.get("sportID"))
    print("NORM SPORT:", norm["sport_id"])
    print("HOME ID:", norm["home_team"]["id"])
    print("HOME NAME:", norm["home_team"]["name"])
    print("LIVE:", norm["live"])
    print("ODDS:", norm["odds_available"])
