#!/usr/bin/env python3
from departments.deportes.futbol.handlers import handle_futbol_ligas_base

data = handle_futbol_ligas_base()
print("PREMIER_COUNT=", len(data.get("premier_league", [])))
if data.get("premier_league"):
    print("PREMIER_FIRST=", data["premier_league"][0])

print("LALIGA_COUNT=", len(data.get("la_liga", [])))
if data.get("la_liga"):
    print("LALIGA_FIRST=", data["la_liga"][0])
