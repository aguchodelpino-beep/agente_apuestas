#!/usr/bin/env python3
from __future__ import annotations
import json
from sharedprovidersportsgameodds import get_leagues, get_events_by_league

res = get_leagues()
print("LEAGUES_STATUS:", res["status_code"])

data = res["data"]
if not isinstance(data, dict) or not isinstance(data.get("data"), list):
    print("No se pudo leer catálogo de ligas")
    raise SystemExit(1)

tennis = [x for x in data["data"] if x.get("sportID") == "TENNIS"]
print("TENNIS_LEAGUES_COUNT:", len(tennis))

for item in tennis[:20]:
    print("-" * 80)
    print("LEAGUE_ID:", item.get("leagueID"))
    print("NAME:", item.get("name"))
    print("LONG_NAME:", item.get("longName"))
    print("COUNTRY:", item.get("countryName"))

print("=" * 80)
print("TESTEANDO PRIMERAS 5 LIGAS TENNIS")
for item in tennis[:5]:
    league_id = item.get("leagueID")
    if not league_id:
        continue
    test = get_events_by_league(league_id, limit=2)
    payload = test["data"]
    count = len(payload.get("data", [])) if isinstance(payload, dict) else 0
    print(f"{league_id} | status={test['status_code']} | count={count}")
