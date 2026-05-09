from __future__ import annotations

from typing import Any

from departments.deportes.futbol import repo
from shared.datetimeutils import daylabel, hourlabel


def row_title(row: dict[str, Any]) -> str:
    home = (
        row.get("home")
        or row.get("home_team")
        or row.get("homeTeam")
        or row.get("player1")
        or row.get("competitor1")
        or "TBD"
    )
    away = (
        row.get("away")
        or row.get("away_team")
        or row.get("awayTeam")
        or row.get("player2")
        or row.get("competitor2")
        or "TBD"
    )
    return f"{home} vs {away}"


def row_tour(row: dict[str, Any]) -> str:
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

    return "Tenis"


def row_start(row: dict[str, Any]) -> str:
    return str(
        row.get("commence_time")
        or row.get("start_time")
        or row.get("start")
        or row.get("date")
        or row.get("event_time")
        or row.get("scheduled")
        or ""
    ).strip()


def day_iso(value: str) -> str:
    if not value:
        return ""
    return value[:10] if len(value) >= 10 else value


def markets_count(row: dict[str, Any]) -> int:
    markets = row.get("markets", [])
    return len(markets) if isinstance(markets, list) else 0


def normalize_card(row: dict[str, Any], index: int) -> dict[str, Any]:
    start_raw = row_start(row)
    return {
        "index": index,
        "fixture_id": row.get("fixture_id"),
        "title": row_title(row),
        "tour": row_tour(row),
        "start": start_raw,
        "day": daylabel(start_raw),
        "day_iso": day_iso(start_raw),
        "hour": hourlabel(start_raw),
        "status": str(row.get("status", "scheduled")).lower(),
        "markets": markets_count(row),
        "source": row.get("source", ""),
        "raw": row,
    }


def list_today_events() -> list[dict[str, Any]]:
    return repo.get_today_events()


def list_upcoming_events(limit: int = 10) -> list[dict[str, Any]]:
    return repo.get_upcoming_events(limit=limit)


def list_events_by_tour(tour: str, limit: int = 10) -> list[dict[str, Any]]:
    return repo.get_events_by_tour(tour=tour, limit=limit)


def build_event_cards(limit: int = 10) -> list[dict[str, Any]]:
    rows = repo.get_upcoming_events(limit=limit)
    return [normalize_card(row, i) for i, row in enumerate(rows, start=1)]


def build_event_groups(limit: int = 10) -> list[dict[str, Any]]:
    cards = build_event_cards(limit=limit)
    grouped: dict[str, list[dict[str, Any]]] = {}

    for card in cards:
        key = card.get("day_iso") or "Sin fecha"
        grouped.setdefault(key, []).append(card)

    result: list[dict[str, Any]] = []
    for day in sorted(grouped.keys()):
        items = sorted(grouped[day], key=lambda x: (x.get("hour") or "", x.get("title") or ""))
        result.append({"day": day, "items": items})
    return result


def build_tour_cards(tour: str, limit: int = 10) -> list[dict[str, Any]]:
    rows = repo.get_events_by_tour(tour=tour, limit=limit)
    return [normalize_card(row, i) for i, row in enumerate(rows, start=1)]
