#!/usr/bin/env python3
from shared.provider_espn import (
    get_soccer_scoreboard,
    get_soccer_standings,
    get_soccer_teams,
    get_nba_scoreboard,
)

tests = [
    ("soccer_scoreboard_eng1", get_soccer_scoreboard("eng.1")),
    ("soccer_standings_eng1", get_soccer_standings("eng.1")),
    ("soccer_teams_eng1", get_soccer_teams("eng.1")),
    ("nba_scoreboard", get_nba_scoreboard()),
]

for name, res in tests:
    print("=" * 70)
    print("TEST=", name)
    print("STATUS=", res["status_code"])
    print("URL=", res["url"])
    data = res["data"]
    if isinstance(data, dict):
        print("TOP_KEYS=", list(data.keys())[:12])
        for key in ("events", "sports", "standings", "team", "teams", "articles"):
            if key in data and isinstance(data[key], list):
                print(f"{key.upper()}_COUNT=", len(data[key]))
