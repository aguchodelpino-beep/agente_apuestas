from __future__ import annotations

from typing import Any

from departments.deportes.tenis.repo import get_tennis_fixtures, get_live_tennis_fixtures, get_tennis_fixture_by_id
from departments.deportes.futbol.repo import get_soccer_fixtures, get_live_soccer_fixtures, get_soccer_fixture_by_id
from departments.deportes.basket.repo import get_basketball_fixtures, get_live_basketball_fixtures, get_basketball_fixture_by_id


def get_fixtures_by_sport(sport: str) -> list[dict[str, Any]]:
    sport = sport.lower().strip()
    if sport == "tenis":
        return get_tennis_fixtures()
    if sport in {"futbol", "fútbol", "soccer"}:
        return get_soccer_fixtures()
    if sport == "basket":
        return get_basketball_fixtures()
    return []


def get_live_fixtures_by_sport(sport: str) -> list[dict[str, Any]]:
    sport = sport.lower().strip()
    if sport == "tenis":
        return get_live_tennis_fixtures()
    if sport in {"futbol", "fútbol", "soccer"}:
        return get_live_soccer_fixtures()
    if sport == "basket":
        return get_live_basketball_fixtures()
    return []


def get_fixture_by_id(sport: str, fixture_id: str) -> dict[str, Any] | None:
    sport = sport.lower().strip()
    if sport == "tenis":
        return get_tennis_fixture_by_id(fixture_id)
    if sport in {"futbol", "fútbol", "soccer"}:
        return get_soccer_fixture_by_id(fixture_id)
    if sport == "basket":
        return get_basketball_fixture_by_id(fixture_id)
    return None
