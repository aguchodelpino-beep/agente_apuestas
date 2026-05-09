#!/usr/bin/env python3
from __future__ import annotations
from sharedprovidersrouter import get_events_for_league
from sharedeventnormalizer import normalize_sgo_event
from sharedoddsnormalizer import normalize_sgo_odds

res = get_events_for_league("NBA", limit=3)
events_raw = res.get("result", {}).get("data", {}).get("data", []) if res.get("ok") else []
picks = []

for raw_event in events_raw:
    event = normalize_sgo_event(raw_event)
    odds = normalize_sgo_odds(event["raw_odds"])
    
    # DraftKings moneyline
    ml_draftkings = [
        o for o in odds
        if o.get("bookmaker_id") == "draftkings"
        and o.get("bet_type_id") == "ml"
    ]
    
    if ml_draftkings:
        home_ml = next((o for o in ml_draftkings if o.get("side_id") == "home"), None)
        away_ml = next((o for o in ml_draftkings if o.get("side_id") == "away"), None)
        
        if home_ml and away_ml:
            picks.append({
                "event_id": event["event_id"],
                "home": event["home_team"]["name"],
                "away": event["away_team"]["name"],
                "live": event["live"],
                "home_ml": home_ml["odds"],
                "away_ml": away_ml["odds"],
                "fair_home": home_ml.get("fair_odds"),
                "fair_away": away_ml.get("fair_odds"),
                "value_home": abs(float(home_ml.get("odds", 0)) - float(home_ml.get("fair_odds", 0))) if home_ml.get("fair_odds") else 0,
            })

print("=" * 80)
print("NBA PICKS (DraftKings ML):", len(picks))
for pick in picks:
    print("-" * 60)
    print(f"{pick['home']} vs {pick['away']}")
    print(f"DraftKings ML: {pick['home_ml']} / {pick['away_ml']}")
    print(f"Fair: {pick['fair_home']} / {pick['fair_away']}")
    print(f"Value Home: {pick['value_home']:.0f}")
