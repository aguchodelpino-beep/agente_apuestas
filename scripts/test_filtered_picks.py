#!/usr/bin/env python3
from __future__ import annotations
from departmentsdeportespickservice import generate_filtered_picks

picks_nba = generate_filtered_picks("NBA", min_edge=0.5, limit=5)
picks_mls = generate_filtered_picks("MLS", min_edge=0.5, limit=5)

print("=" * 80)
print("NBA FILTERED PICKS (edge 0.5%+):", len(picks_nba))
for pick in picks_nba:
    print("-" * 60)
    print(f"{pick['match']} | {pick['best_side'].upper()}")
    print(f"Book: {pick['bookmaker']} | {pick['book_odds']} | Edge: {pick['edge_percent']}%")
    print(f"Probs: {pick['book_prob']}% vs {pick['fair_prob']}%")

print("\n" + "=" * 80)
print("MLS FILTERED PICKS (edge 0.5%+):", len(picks_mls))
for pick in picks_mls:
    print("-" * 60)
    print(f"{pick['match']} | {pick['best_side'].upper()}")
    print(f"Book: {pick['bookmaker']} | {pick['book_odds']} | Edge: {pick['edge_percent']}%")
    print(f"Probs: {pick['book_prob']}% vs {pick['fair_prob']}%")
