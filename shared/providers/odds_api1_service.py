from __future__ import annotations

from typing import Any

from shared.providers.odds_api1_client import fetch_fixtures_by_sport
from shared.providers.odds_api1_normalize import normalize_odds_api1_fixture


SPORT_ID_TENNIS = 12
SPORT_ID_SOCCER = 10
SPORT_ID_BASKETBALL = 11


def fetch_normalized_fixtures_by_sport(sport_id: int) -> list[dict[str, Any]]:
    raw_items = fetch_fixtures_by_sport(sport_id)
    return [normalize_odds_api1_fixture(item) for item in raw_items]


def fetch_tennis_fixtures() -> list[dict[str, Any]]:
    return fetch_normalized_fixtures_by_sport(SPORT_ID_TENNIS)


def fetch_soccer_fixtures() -> list[dict[str, Any]]:
    return fetch_normalized_fixtures_by_sport(SPORT_ID_SOCCER)


def fetch_basketball_fixtures() -> list[dict[str, Any]]:
    return fetch_normalized_fixtures_by_sport(SPORT_ID_BASKETBALL)
