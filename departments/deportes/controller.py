from __future__ import annotations

from departments.deportes.service import get_fixtures_by_sport, get_live_fixtures_by_sport, get_fixture_by_id


def list_sport(sport: str):
    return get_fixtures_by_sport(sport)


def list_live_sport(sport: str):
    return get_live_fixtures_by_sport(sport)


def detail_sport_fixture(sport: str, fixture_id: str):
    return get_fixture_by_id(sport, fixture_id)
