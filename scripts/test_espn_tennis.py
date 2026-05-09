#!/usr/bin/env python3
from shared.provider_espn import (
    get_tennis_scoreboard,
    get_tennis_news,
    get_tennis_teams_like_listing,
)

tests = [
    ("tennis_scoreboard_atp", get_tennis_scoreboard()),
    ("tennis_news_atp", get_tennis_news()),
    ("tennis_teams_atp", get_tennis_teams_like_listing()),
]

for name, res in tests:
    print("=" * 70)
    print("TEST=", name)
    print("STATUS=", res["status_code"])
    print("URL=", res["url"])
    data = res["data"]

    if isinstance(data, dict):
        print("TOP_KEYS=", list(data.keys())[:12])
        for key in ("events", "articles", "sports", "leagues"):
            if key in data and isinstance(data[key], list):
                print(f"{key.upper()}_COUNT=", len(data[key]))
    elif isinstance(data, list):
        print("COUNT=", len(data))
        if data:
            print("FIRST=", str(data[0])[:300])
    else:
        print("RAW=", str(data)[:300])
