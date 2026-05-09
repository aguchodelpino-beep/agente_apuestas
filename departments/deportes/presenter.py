from __future__ import annotations

from typing import Any


def format_fixture_brief(item: dict[str, Any]) -> str:
    sport = item.get("sport_name", "?")
    league = item.get("league_name", "?")
    home = item.get("home", "?")
    away = item.get("away", "?")
    status = item.get("status_name", "?")
    live = "LIVE" if item.get("live") else "PRE"
    books = ", ".join(item.get("odds_bookmakers", [])) or "sin_bookmaker"
    return f"[{sport}] {home} vs {away} | {league} | {status} | {live} | odds: {books}"


def format_fixture_list(items: list[dict[str, Any]], limit: int = 5) -> list[str]:
    return [format_fixture_brief(item) for item in items[:limit]]
