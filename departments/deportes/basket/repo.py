from __future__ import annotations

from typing import Any

from shared.cache import load_sport_day
from shared.datetime_utils import today_str

SPORT = "basket"


def _row_start(row: dict[str, Any]) -> str:
    return str(
        row.get("commence_time")
        or row.get("start_time")
        or row.get("start")
        or row.get("date")
        or row.get("event_time")
        or row.get("scheduled")
        or ""
    ).strip()


def _row_tour(row: dict[str, Any]) -> str:
    league = row.get("league")
    if isinstance(league, str) and league.strip():
        return league.strip()

    tournament = row.get("tournament")
    if isinstance(tournament, str) and tournament.strip():
        return tournament.strip()

    raw = row.get("raw")
    if isinstance(raw, dict):
        for key in ("shortName", "name", "eventName", "tournament"):
            value = raw.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    return "Basket"


def _row_title(row: dict[str, Any]) -> str:
    home = (
        row.get("home")
        or row.get("home_team")
        or row.get("player_1")
        or row.get("competitor_1")
        or "TBD"
    )
    away = (
        row.get("away")
        or row.get("away_team")
        or row.get("player_2")
        or row.get("competitor_2")
        or "TBD"
    )
    return f"{home} vs {away}"


def _sorted_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda row: (_row_start(row), _row_tour(row), _row_title(row)))


def list_fixtures() -> list[dict[str, Any]]:
    return load_sport_day(SPORT, today_str())


def list_live_fixtures() -> list[dict[str, Any]]:
    return [item for item in list_fixtures() if item.get("live") is True]


def get_fixture_by_id(fixture_id: str) -> dict[str, Any] | None:
    for item in list_fixtures():
        if item.get("fixture_id") == fixture_id:
            return item
    return None


def get_today_events() -> list[dict[str, Any]]:
    today = today_str()
    rows = []
    for item in list_fixtures():
        start = _row_start(item)
        if not start or start.startswith(today):
            rows.append(item)
    return _sorted_rows(rows)


def get_upcoming_events(limit: int = 10) -> list[dict[str, Any]]:
    rows = _sorted_rows(list_fixtures())
    if limit <= 0:
        return rows
    return rows[:limit]


def get_events_by_tour(tour: str, limit: int = 10) -> list[dict[str, Any]]:
    needle = (tour or "").strip().lower()
    if not needle:
        return get_upcoming_events(limit=limit)

    rows = [item for item in list_fixtures() if needle in _row_tour(item).lower()]
    rows = _sorted_rows(rows)
    if limit <= 0:
        return rows
    return rows[:limit]
