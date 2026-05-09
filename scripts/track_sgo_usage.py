#!/usr/bin/env python3
"""Simulate SGO usage tracking (no real API call)."""

from scripts.api_cost_dashboard import track_usage

# Simulate SGO usage (replace with real headers when calling API)
track_usage("sportsgameodds", used=5, remaining=995, total_limit=1000)
track_usage("oddsapi", used=2, remaining=498, total_limit=500)
track_usage("rapidapi", used=1, remaining=999, total_limit=1000)

print("✅ Usage tracked (simulation)")
print("Run: PYTHONPATH=. venv/bin/python3 scripts/api_cost_dashboard.py")
