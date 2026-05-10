#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from scripts.priority_leagues import TOP_EUROPE_FOOTBALL, TOP_BASKET

TODAY = datetime.utcnow().strftime("%Y-%m-%d")
BASE = Path("data/raw")


def fetch_stub_rows(league_key: str) -> list[dict]:
    rows = []
    for i in range(1, 6):
        rows.append(
            {
                "fixture_id": f"{league_key}_{i}",
                "league": league_key,
                "home": "TBD",
                "away": "TBD",
                "status": "scheduled",
                "live": False,
                "commence_time": f"{TODAY}T0{i}:00:00Z",
                "_sport_key": league_key,
                "_source": "priority_stub",
            }
        )
    return rows


def save_rows(sport: str, rows: list[dict]) -> None:
    out = BASE / sport / f"{TODAY}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"SAVED {sport}: {len(rows)} -> {out}")


def main() -> None:
    print("🔄 Refresh ligas prioritarias...")
    print(f"Target: {len(TOP_EUROPE_FOOTBALL) + len(TOP_BASKET)} ligas")

    futbol_rows = []
    for league in TOP_EUROPE_FOOTBALL:
        try:
            futbol_rows.extend(fetch_stub_rows(league))
        except Exception as e:
            print(f"❌ futbol {league}: {e}")

    basket_rows = []
    for league in TOP_BASKET:
        try:
            basket_rows.extend(fetch_stub_rows(league))
        except Exception as e:
            print(f"❌ basket {league}: {e}")

    save_rows("futbol", futbol_rows)
    save_rows("basket", basket_rows)
    print("🎯 Ligas prioritarias cacheadas")


if __name__ == "__main__":
    main()
