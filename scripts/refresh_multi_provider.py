#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

TODAY = datetime.utcnow().strftime("%Y-%m-%d")
BASE = Path("data/raw")


def normalize_row(row: dict, source: str, sport: str) -> dict:
    return {
        "fixture_id": str(row.get("fixture_id") or row.get("id") or ""),
        "league": str(
            row.get("league")
            or row.get("tournament")
            or row.get("competition")
            or row.get("sport_nice")
            or ""
        ).strip(),
        "home": row.get("home") or row.get("home_team") or row.get("team1") or "TBD",
        "away": row.get("away") or row.get("away_team") or row.get("team2") or "TBD",
        "status": str(row.get("status") or "scheduled").lower(),
        "live": bool(
            row.get("live") is True
            or str(row.get("status", "")).lower() in {"live", "inplay", "in_progress"}
        ),
        "commence_time": row.get("commence_time") or row.get("start_time") or row.get("date") or "",
        "_source": source,
        "_sport": sport,
        "raw": row,
    }


def fetch_oddsapi(sport: str) -> list[dict]:
    return []


def fetch_espn(sport: str) -> list[dict]:
    return []


def fetch_pinnacle(sport: str) -> list[dict]:
    return []


def merge_rows(*groups: list[dict]) -> list[dict]:
    dedup: dict[str, dict] = {}
    for group in groups:
        for row in group:
            fid = row.get("fixture_id") or ""
            if fid:
                dedup[fid] = row
    return list(dedup.values())


def save_sport(sport: str, rows: list[dict]) -> None:
    out = BASE / sport / f"{TODAY}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"SAVED {sport}: {len(rows)} -> {out}")


def main() -> None:
    for sport in ("futbol", "basket"):
        odds = [normalize_row(x, "oddsapi", sport) for x in fetch_oddsapi(sport)]
        espn = [normalize_row(x, "espn", sport) for x in fetch_espn(sport)]
        pinnacle = [normalize_row(x, "pinnacle", sport) for x in fetch_pinnacle(sport)]
        final_rows = merge_rows(odds, espn, pinnacle)
        save_sport(sport, final_rows)


if __name__ == "__main__":
    main()
