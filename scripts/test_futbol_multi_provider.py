#!/usr/bin/env python3
from departments.deportes.futbol.repo import FutbolRepo

repo = FutbolRepo()

premier = repo.get_premier_league()
print("PREMIER_COUNT=", len(premier))
if premier:
    print("PREMIER_FIRST=", premier[0])

comps = repo.get_competitions()
print("COMP_STATUS=", comps["status_code"])
print("COMP_URL=", comps["url"])
print("COMP_KEYS=", list(comps["data"].keys())[:10])

matches = repo.get_premier_matches()
print("MATCH_STATUS=", matches["status_code"])
print("MATCH_URL=", matches["url"])
print("MATCH_KEYS=", list(matches["data"].keys())[:10])

m = matches["data"].get("matches", [])
print("MATCH_COUNT=", len(m))
if m:
    first = m[0]
    print("FIRST_MATCH_HOME=", first.get("homeTeam", {}).get("name"))
    print("FIRST_MATCH_AWAY=", first.get("awayTeam", {}).get("name"))
    print("FIRST_MATCH_STATUS=", first.get("status"))
