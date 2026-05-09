#!/usr/bin/env python3
from __future__ import annotations
from departmentsdeportesbasketservice import get_eventos_basket
from departmentsdeportesfutbolservice import get_eventos_futbol

basket = get_eventos_basket(2)
futbol = get_eventos_futbol(2)

print("=" * 80)
print("BASKET_COUNT:", len(basket))
if basket:
    ev = basket[0]
    print("BASKET_EVENT:", ev.get("eventID"))
    print("BASKET_LEAGUE:", ev.get("leagueID"))
    print("BASKET_SPORT:", ev.get("sportID"))
    print("BASKET_LIVE:", ev.get("status", {}).get("live"))

print("=" * 80)
print("FUTBOL_COUNT:", len(futbol))
if futbol:
    ev = futbol[0]
    print("FUTBOL_EVENT:", ev.get("eventID"))
    print("FUTBOL_LEAGUE:", ev.get("leagueID"))
    print("FUTBOL_SPORT:", ev.get("sportID"))
    print("FUTBOL_LIVE:", ev.get("status", {}).get("live"))
