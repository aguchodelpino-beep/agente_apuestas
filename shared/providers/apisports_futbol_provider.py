from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from shared.provider_api_sports import (
    find_league_id_by_name,
    get_fixtures,
    extract_response_items,
)

UTC = timezone.utc

TARGETS = [
    {
        "country": "Ecuador",
        "searches": ["Campeonato Serie A", "Liga Pro", "Liga Pro Serie A", "Serie A"],
        "fallback_name": "LigaPro Ecuador",
    },
    {
        "country": "Colombia",
        "searches": ["Primera A", "Categoria Primera A", "Categoría Primera A", "Liga BetPlay"],
        "fallback_name": "Primera A Colombia",
    },
]


def _season_for_today() -> int:
    return datetime.now(UTC).year


def _map_status(short: str) -> str:
    if short in {"1H", "2H", "HT", "ET", "BT", "P", "LIVE", "INT"}:
        return "live"
    if short in {"FT", "AET", "PEN"}:
        return "finished"
    return "scheduled"


def _pick_best_league(target: dict[str, Any], season: int) -> dict[str, Any] | None:
    for search in target["searches"]:
        matches = find_league_id_by_name(search_text=search, country=target["country"], season=season)
        if not matches:
            matches = find_league_id_by_name(search_text=search, country=target["country"], season=None)
        if matches:
            print(f"[apisports_futbol_provider] match {target['country']} / {search} -> {matches[0]}")
            return matches[0]
    return None


def _norm_fixture(row: dict[str, Any], league_name: str) -> dict[str, Any]:
    fixture = row.get("fixture") or {}
    teams = row.get("teams") or {}
    status_short = ((fixture.get("status") or {}).get("short")) or "NS"
    return {
        "fixture_id": str(fixture.get("id") or ""),
        "sport": "futbol",
        "league": league_name,
        "sport_key": "api_sports",
        "home": ((teams.get("home") or {}).get("name")) or "TBD",
        "away": ((teams.get("away") or {}).get("name")) or "TBD",
        "start_time": fixture.get("date") or datetime.now(UTC).isoformat(),
        "status": _map_status(status_short),
        "source": "apisports",
        "markets": [],
        "raw": row,
    }


def _fetch_league_fixtures(league_id: int, league_name: str, season: int) -> list[dict[str, Any]]:
    payload = get_fixtures(league=league_id, season=season, next_n=20)
    rows = extract_response_items(payload)
    return [_norm_fixture(row, league_name) for row in rows if isinstance(row, dict)]


def fetch_extra_futbol_events() -> list[dict[str, Any]]:
    season = _season_for_today()
    results: list[dict[str, Any]] = []

    for target in TARGETS:
        try:
            league = _pick_best_league(target, season)
            if not league:
                print(f"[apisports_futbol_provider] sin liga para {target['country']} -> {target['searches']}")
                continue

            league_id = int(league["league_id"])
            league_name = str(league.get("league_name") or target["fallback_name"])
            rows = _fetch_league_fixtures(league_id=league_id, league_name=league_name, season=season)

            if not rows and season > 2024:
                rows = _fetch_league_fixtures(league_id=league_id, league_name=league_name, season=season - 1)

            print(f"[apisports_futbol_provider] {league_name} ({league_id}) -> {len(rows)}")
            results.extend(rows)

        except Exception as exc:
            print(f"[apisports_futbol_provider] {target['country']}: {exc}")

    return results


if __name__ == "__main__":
    print("SCRIPT OK")
