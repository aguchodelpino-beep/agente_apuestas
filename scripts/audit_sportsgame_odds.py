#!/usr/bin/env python3
from __future__ import annotations
import json
import requests
from core.config import Config

BASES = [
    "https://api.sportsgameodds.com",
    "https://sportsgameodds.com",
]

PATHS = [
    "/v1/sports",
    "/v1/leagues",
    "/v1/bookmakers",
    "/sports",
    "/leagues",
    "/bookmakers",
    "/api/v1/sports",
    "/api/v1/leagues",
    "/api/v1/bookmakers",
]

HEADERS_CANDIDATES = [
    {"x-api-key": Config.SPORTSGAME_ODDS_KEY, "accept": "application/json"},
    {"X-API-Key": Config.SPORTSGAME_ODDS_KEY, "accept": "application/json"},
    {"apikey": Config.SPORTSGAME_ODDS_KEY, "accept": "application/json"},
    {"Authorization": f"Bearer {Config.SPORTSGAME_ODDS_KEY}", "accept": "application/json"},
]

results = []

for base in BASES:
    for path in PATHS:
        for headers in HEADERS_CANDIDATES:
            url = f"{base}{path}"
            label = ",".join(headers.keys())
            try:
                r = requests.get(url, headers=headers, timeout=20)
                try:
                    data = r.json()
                except Exception:
                    data = {"raw_text": r.text[:300]}
                results.append({
                    "url": url,
                    "header_keys": list(headers.keys()),
                    "status": r.status_code,
                    "top_keys": list(data.keys())[:10] if isinstance(data, dict) else [],
                    "body_preview": json.dumps(data)[:300] if isinstance(data, (dict, list)) else str(data)[:300],
                })
                print(f"{r.status_code:>3} | {label:<30} | {url}")
            except Exception as e:
                results.append({
                    "url": url,
                    "header_keys": list(headers.keys()),
                    "status": "ERROR",
                    "error": repr(e),
                })
                print(f"ERR | {label:<30} | {url} | {e}")

ok = [x for x in results if x.get("status") == 200]
print("\nOK_COUNT=", len(ok))

with open("sportsgameodds_audit.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Guardado: sportsgameodds_audit.json")
