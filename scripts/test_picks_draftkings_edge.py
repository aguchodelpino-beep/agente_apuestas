#!/usr/bin/env python3
from __future__ import annotations
from sharedprovidersrouter import get_events_for_league
from sharedeventnormalizer import normalize_sgo_event
from sharedoddsnormalizer import normalize_sgo_odds
from sharedoddsmath import american_to_prob, prob_to_percent, edge_percent

res = get_events_for_league("NBA", limit=3)
events_raw = res.get("result", {}).get("data", {}).get("data", []) if res.get("ok") else []

picks = []

for raw_event in events_raw:
    event = normalize_sgo_event(raw_event)
    odds = normalize_sgo_odds(event["raw_odds"])

    ml_draftkings = [
        o for o in odds
        if o.get("bookmaker_id") == "draftkings"
        and o.get("bet_type_id") == "ml"
    ]

    home_ml = next((o for o in ml_draftkings if o.get("side_id") == "home"), None)
    away_ml = next((o for o in ml_draftkings if o.get("side_id") == "away"), None)

    if home_ml and away_ml:
        picks.append({
            "match": f"{event['home_team']['name']} vs {event['away_team']['name']}",
            "home_book": home_ml["odds"],
            "home_fair": home_ml.get("fair_odds"),
            "home_book_prob": prob_to_percent(american_to_prob(home_ml["odds"])),
            "home_fair_prob": prob_to_percent(american_to_prob(home_ml.get("fair_odds"))),
            "home_edge": edge_percent(home_ml["odds"], home_ml.get("fair_odds")),
            "away_book": away_ml["odds"],
            "away_fair": away_ml.get("fair_odds"),
            "away_book_prob": prob_to_percent(american_to_prob(away_ml["odds"])),
            "away_fair_prob": prob_to_percent(american_to_prob(away_ml.get("fair_odds"))),
            "away_edge": edge_percent(away_ml["odds"], away_ml.get("fair_odds")),
        })

print("=" * 80)
print("NBA PICKS EDGE:", len(picks))
for pick in picks:
    print("-" * 60)
    print(pick["match"])
    print(f"HOME book/fair: {pick['home_book']} / {pick['home_fair']}")
    print(f"HOME prob book/fair: {pick['home_book_prob']}% / {pick['home_fair_prob']}%")
    print(f"HOME edge: {pick['home_edge']}%")
    print(f"AWAY book/fair: {pick['away_book']} / {pick['away_fair']}")
    print(f"AWAY prob book/fair: {pick['away_book_prob']}% / {pick['away_fair_prob']}%")
    print(f"AWAY edge: {pick['away_edge']}%")
