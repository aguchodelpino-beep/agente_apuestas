#!/usr/bin/env python3
from shared.provider_api_sports import (
    get_status,
    find_league_id_by_name,
    list_fixtures_by_league,
)

status = get_status()
print("STATUS_CODE=", status["status_code"])
print("STATUS_URL=", status["url"])

premier = find_league_id_by_name("Premier League", country="England")
print("PREMIER_MATCHES=", len(premier))
if premier:
    print("PREMIER_FIRST=", premier[0])

laliga = find_league_id_by_name("La Liga", country="Spain")
print("LALIGA_MATCHES=", len(laliga))
if laliga:
    print("LALIGA_FIRST=", laliga[0])

fixtures_last = list_fixtures_by_league(league=39, season=2024, last_n=5)
print("FIXTURES_39_2024_LAST_COUNT=", len(fixtures_last))
if fixtures_last:
    print("FIXTURE_LAST_FIRST=", fixtures_last[0])

fixtures_next = list_fixtures_by_league(league=39, season=2024, next_n=5)
print("FIXTURES_39_2024_NEXT_COUNT=", len(fixtures_next))
if fixtures_next:
    print("FIXTURE_NEXT_FIRST=", fixtures_next[0])
