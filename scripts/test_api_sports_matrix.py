#!/usr/bin/env python3
from shared.provider_api_sports import api_sports_get

tests = [
    ("status", "/status", {}),
    ("leagues_2025", "/leagues", {"season": 2025}),
    ("leagues_2024", "/leagues", {"season": 2024}),
    ("leagues_all", "/leagues", {}),
    ("leagues_england", "/leagues", {"country": "England"}),
    ("leagues_spain", "/leagues", {"country": "Spain"}),
    ("leagues_query_premier", "/leagues", {"search": "Premier League"}),
    ("fixtures_next_39", "/fixtures", {"league": 39, "season": 2025, "next": 5}),
]

for name, path, params in tests:
    res = api_sports_get(path, params=params)
    data = res["data"]
    response = data.get("response") if isinstance(data, dict) else None

    print("=" * 70)
    print("TEST=", name)
    print("STATUS=", res["status_code"])
    print("URL=", res["url"])
    print("RESPONSE_TYPE=", type(response).__name__)

    if isinstance(response, list):
        print("COUNT=", len(response))
        if response:
            first = response[0]
            if isinstance(first, dict):
                print("FIRST_KEYS=", list(first.keys())[:10])
                if "league" in first:
                    print("LEAGUE_NAME=", first.get("league", {}).get("name"))
                    print("COUNTRY=", first.get("country", {}).get("name"))
                if "fixture" in first:
                    print("FIXTURE_ID=", first.get("fixture", {}).get("id"))
                    teams = first.get("teams", {})
                    print("MATCH=", teams.get("home", {}).get("name"), "vs", teams.get("away", {}).get("name"))
    elif isinstance(response, dict):
        print("COUNT=", len(response))
        print("DICT_KEYS=", list(response.keys())[:15])
    else:
        print("COUNT= 0")
        print("RAW_RESPONSE=", str(response)[:300])
