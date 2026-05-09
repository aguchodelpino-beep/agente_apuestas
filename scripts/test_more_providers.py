#!/usr/bin/env python3
from shared.provider_sportsgame_odds import sgo_get
from shared.provider_football_data import football_data_get

tests = [
    ("sgo_sports", lambda: sgo_get("/v1/sports")),
    ("sgo_leagues", lambda: sgo_get("/v1/leagues")),
    ("sgo_bookmakers", lambda: sgo_get("/v1/bookmakers")),
    ("fd_competitions", lambda: football_data_get("/competitions")),
    ("fd_matches_pl", lambda: football_data_get("/competitions/PL/matches")),
]

for name, fn in tests:
    print("=" * 70)
    print("TEST=", name)
    try:
        res = fn()
        print("STATUS=", res["status_code"])
        print("URL=", res["url"])
        data = res["data"]
        if isinstance(data, dict):
            print("TOP_KEYS=", list(data.keys())[:12])
            for k in ("count", "results", "success"):
                if k in data:
                    print(f"{k.upper()}=", data[k])
        elif isinstance(data, list):
            print("COUNT=", len(data))
            if data:
                print("FIRST=", str(data[0])[:300])
        else:
            print("RAW=", str(data)[:300])
    except Exception as e:
        print("ERROR=", repr(e))
