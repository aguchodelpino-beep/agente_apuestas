#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from shared.providers.oddsapi_client import fetch_fixtures

TODAY = datetime.utcnow().strftime("%Y-%m-%d")
BASE = Path("data/raw")

PRIORITY = {
    "futbol": [
        "soccer_epl",
        "soccer_spain_la_liga",
        "soccer_germany_bundesliga",
        "soccer_italy_serie_a",
        "soccer_france_ligue_one",
        "soccer_netherlands_eredivisie",
        "soccer_portugal_primeira_liga",
        "soccer_russia_premier_league",
        "soccer_uefa_champs_league",
        "soccer_uefa_europa_league",
        "soccer_uefa_europa_conference_league",
        "soccer_fa_cup",
        "soccer_germany_dfb_pokal",
        "soccer_italy_coppa_italia",
        "soccer_france_coupe_de_france",
        "soccer_brazil_campeonato",
        "soccer_argentina_primera_division",
        "soccer_mexico_ligamx",
        "soccer_colombia_primera_a",
        "soccer_chile_campeonato",
        "soccer_ecuador_liga_pro",
        "soccer_conmebol_copa_libertadores",
        "soccer_conmebol_copa_sudamericana",
        "soccer_usa_mls",
        "soccer_saudi_arabia_pro_league",
        "soccer_japan_j_league",
        "soccer_china_superleague",
        "soccer_korea_kleague1",
        "soccer_australia_aleague",
    ],
    "basket": [
        "basketball_nba",
        "basketball_euroleague",
        "basketball_wnba",
    ],
}

def outpath(sport: str) -> Path:
    p = BASE / sport / f"{TODAY}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

def main() -> None:
    print(f"REFRESH UTC DAY: {TODAY}")
    total_saved = 0

    for sport, sport_keys in PRIORITY.items():
        merged: list[dict] = []
        print(f"\n=== {sport.upper()} ===")

        for sport_key in sport_keys:
            try:
                rows = fetch_fixtures(sport_key)
                print(f"{sport_key}: {len(rows)}")
                for row in rows:
                    row["_source"] = "oddsapi"
                    row["_sport_key"] = sport_key
                merged.extend(rows)
            except Exception as e:
                print(f"{sport_key}: ERROR {e}")

        dedup = {}
        for row in merged:
            fid = row.get("id")
            if fid:
                dedup[fid] = row

        final_rows = list(dedup.values())
        path = outpath(sport)
        path.write_text(json.dumps(final_rows, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"SAVED {sport}: {len(final_rows)} -> {path}")
        total_saved += len(final_rows)

    print(f"\nTOTAL SAVED: {total_saved}")

if __name__ == "__main__":
    main()
