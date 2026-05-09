#!/usr/bin/env python3
from shared.provider_api_sports import get_status, get_leagues

s = get_status()
print("STATUS_CODE_STATUS=", s["status_code"])
print("URL_STATUS=", s["url"])

data = s["data"]
if isinstance(data, dict):
    print("STATUS_KEYS=", list(data.keys())[:10])

l = get_leagues()
print("STATUS_CODE_LEAGUES=", l["status_code"])
print("URL_LEAGUES=", l["url"])

ldata = l["data"]
if isinstance(ldata, dict):
    resp = ldata.get("response", [])
    print("LEAGUES_COUNT=", len(resp))
    if resp:
        first = resp[0]
        league = first.get("league", {})
        country = first.get("country", {})
        print("FIRST_LEAGUE=", league.get("name"))
        print("FIRST_COUNTRY=", country.get("name"))
