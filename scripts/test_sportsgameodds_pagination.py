#!/usr/bin/env python3
from __future__ import annotations
from sharedprovidersportsgameodds import get_events_by_league

res1 = get_events_by_league("NBA", limit=1)
print("PAGE1_STATUS:", res1["status_code"])
data1 = res1["data"]
cursor = data1.get("nextCursor") if isinstance(data1, dict) else None
print("PAGE1_CURSOR:", cursor)
print("PAGE1_COUNT:", len(data1.get("data", [])) if isinstance(data1, dict) else 0)

if cursor:
    res2 = get_events_by_league("NBA", limit=1, cursor=cursor)
    print("PAGE2_STATUS:", res2["status_code"])
    data2 = res2["data"]
    print("PAGE2_COUNT:", len(data2.get("data", [])) if isinstance(data2, dict) else 0)
