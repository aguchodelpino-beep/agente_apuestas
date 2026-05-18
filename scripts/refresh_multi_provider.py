#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from shared.providers.futbol_provider import fetch_futbol_events
from shared.providers.tenis_provider import fetch_tennis_events
from shared.providers.basket_provider import fetch_basket_events
from shared.provider_theodds_api import get_odds, get_active_tennis_keys

UTC = timezone.utc
NOW = lambda: datetime.now(UTC)
TODAY = NOW().strftime("%Y-%m-%d")
BASE = Path("data/raw")
CACHE_DIARIO = Path("cache_diario")

FOOTBALL_KEYS = [
    "soccer_epl",
    "soccer_spain_la_liga",
    "soccer_germany_bundesliga",
    "soccer_italy_serie_a",
    "soccer_france_ligue_one",
    "soccer_netherlands_eredivisie",
    "soccer_portugal_primeira_liga",
    "soccer_uefa_champs_league",
    "soccer_uefa_europa_league",
    "soccer_uefa_europa_conference_league",
    "soccer_brazil_campeonato",
    "soccer_argentina_primera_division",
    "soccer_mexico_ligamx",
    "soccer_colombia_primera_a",
    "soccer_ecuador_liga_pro",
    "soccer_conmebol_copa_libertadores",
    "soccer_conmebol_copa_sudamericana",
    "soccer_usa_mls",
]
BASKET_KEYS = ["basketball_nba", "basketball_wnba", "basketball_euroleague"]


def _atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def _norm_row(row: dict[str, Any], source: str, sport: str) -> dict[str, Any]:
    fixture_id = str(row.get("fixture_id") or row.get("id") or "")
    league = str(
        row.get("league")
        or row.get("tournament")
        or row.get("competition")
        or row.get("sport_nice")
        or row.get("sport_key")
        or row.get("league_name")
        or ""
    ).strip()
    home = row.get("home") or row.get("home_team") or row.get("team1") or "TBD"
    away = row.get("away") or row.get("away_team") or row.get("team2") or "TBD"
    start = row.get("commence_time") or row.get("start_time") or row.get("date") or ""
    status = str(row.get("status") or "scheduled").lower()
    return {
        "fixture_id": fixture_id or f"{sport}|{league}|{home}|{away}|{start}",
        "league": league,
        "home": home,
        "away": away,
        "status": status,
        "live": bool(row.get("live") is True or status in {"live", "inplay", "in_progress"}),
        "commence_time": start,
        "_source": source,
        "_sport": sport,
        "raw": row,
    }


def _norm_odds_event(ev: dict[str, Any], sport: str, sport_key: str) -> dict[str, Any]:
    return _norm_row(
        {
            "id": ev.get("id"),
            "league": sport_key,
            "home_team": ev.get("home_team"),
            "away_team": ev.get("away_team"),
            "commence_time": ev.get("commence_time"),
            "status": "scheduled",
            "sport_key": sport_key,
            "bookmakers": ev.get("bookmakers", []),
        },
        "oddsapi",
        sport,
    )


def _dedupe(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = row.get("fixture_id") or ""
        if not key:
            continue
        if key not in merged:
            merged[key] = row
            continue
        cur = merged[key]
        if cur.get("_source") == "oddsapi" and row.get("_source") != "oddsapi":
            merged[key] = row
        elif not cur.get("league") and row.get("league"):
            merged[key] = {**cur, **row}
    out = list(merged.values())
    out.sort(key=lambda x: x.get("commence_time") or "")
    return out


def _save_sport(sport: str, rows: list[dict[str, Any]]) -> int:
    payload = _dedupe(rows)
    day_path = BASE / sport / f"{TODAY}.json"
    latest_path = BASE / sport / "latest.json"
    diario_path = CACHE_DIARIO / f"cache{sport}.json"

    _atomic_write_json(day_path, payload)
    _atomic_write_json(latest_path, payload)
    _atomic_write_json(
        diario_path,
        {
            "sport": sport,
            "date": TODAY,
            "updated_at": NOW().isoformat(),
            "count": len(payload),
            "items": payload,
        },
    )
    print(f"SAVED {sport}: raw={len(rows)} dedupe={len(payload)} -> {day_path}")
    return len(payload)


def _safe_fetch(label: str, fn: Callable[[], list[dict[str, Any]]]) -> tuple[list[dict[str, Any]], str | None]:
    try:
        rows = fn()
        return rows, None
    except Exception as exc:
        return [], f"{label}: {exc}"


def fetch_oddsapi_futbol() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key in FOOTBALL_KEYS:
        try:
            data = get_odds(key, regions="us,eu", markets="h2h,spreads,totals")
            rows.extend(_norm_odds_event(ev, "futbol", key) for ev in data)
        except Exception as exc:
            print(f"[oddsapi:futbol] {key}: {exc}")
    return rows


def fetch_oddsapi_basket() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key in BASKET_KEYS:
        try:
            data = get_odds(key, regions="us,eu", markets="h2h,spreads,totals")
            rows.extend(_norm_odds_event(ev, "basket", key) for ev in data)
        except Exception as exc:
            print(f"[oddsapi:basket] {key}: {exc}")
    return rows


def fetch_oddsapi_tenis() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        keys = get_active_tennis_keys()
    except Exception as exc:
        print(f"[oddsapi:tenis] active keys: {exc}")
        return rows
    for key in keys:
        try:
            data = get_odds(key, regions="us,eu", markets="h2h")
            rows.extend(_norm_odds_event(ev, "tenis", key) for ev in data)
        except Exception as exc:
            print(f"[oddsapi:tenis] {key}: {exc}")
    return rows


def build_daily_events() -> dict[str, Any]:
    summary: dict[str, Any] = {
        "date": TODAY,
        "generated_at": NOW().isoformat(),
        "sports": {},
        "errors": [],
    }

    futbol_base, err = _safe_fetch("fetch_futbol_events", fetch_futbol_events)
    if err:
        summary["errors"].append(err)
    futbol_odds, _ = _safe_fetch("fetch_oddsapi_futbol", fetch_oddsapi_futbol)
    futbol_rows = [_norm_row(x, x.get("source", "provider"), "futbol") for x in futbol_base] + futbol_odds
    futbol_count = _save_sport("futbol", futbol_rows)
    summary["sports"]["futbol"] = {
        "provider_base": len(futbol_base),
        "provider_oddsapi": len(futbol_odds),
        "raw_total": len(futbol_rows),
        "saved_total": futbol_count,
    }

    basket_base, err = _safe_fetch("fetch_basket_events", fetch_basket_events)
    if err:
        summary["errors"].append(err)
    basket_odds, _ = _safe_fetch("fetch_oddsapi_basket", fetch_oddsapi_basket)
    basket_rows = [_norm_row(x, x.get("source", "provider"), "basket") for x in basket_base] + basket_odds
    basket_count = _save_sport("basket", basket_rows)
    summary["sports"]["basket"] = {
        "provider_base": len(basket_base),
        "provider_oddsapi": len(basket_odds),
        "raw_total": len(basket_rows),
        "saved_total": basket_count,
    }

    tenis_base, err = _safe_fetch("fetch_tennis_events", fetch_tennis_events)
    if err:
        summary["errors"].append(err)
    tenis_odds, _ = _safe_fetch("fetch_oddsapi_tenis", fetch_oddsapi_tenis)
    tenis_rows = [_norm_row(x, x.get("source", "provider"), "tenis") for x in tenis_base] + tenis_odds
    tenis_count = _save_sport("tenis", tenis_rows)
    summary["sports"]["tenis"] = {
        "provider_base": len(tenis_base),
        "provider_oddsapi": len(tenis_odds),
        "raw_total": len(tenis_rows),
        "saved_total": tenis_count,
    }

    return summary


if __name__ == "__main__":
    print(json.dumps(build_daily_events(), ensure_ascii=False, indent=2))
