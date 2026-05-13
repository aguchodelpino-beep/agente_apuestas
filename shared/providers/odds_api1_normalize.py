from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class NormalizedFixture:
    fixture_id: str | None
    sport_id: int | None
    sport_name: str | None
    league_id: int | None
    league_name: str | None
    category_name: str | None
    home: str | None
    away: str | None
    live: bool | None
    status_id: int | None
    status_name: str | None
    participant1_abbr: str | None
    participant2_abbr: str | None
    odds_bookmakers: list[str]
    raw: dict[str, Any]


def normalize_odds_api1_fixture(item: dict[str, Any]) -> dict[str, Any]:
    sport = item.get("sport") or {}
    tournament = item.get("tournament") or {}
    participants = item.get("participants") or {}
    status = item.get("status") or {}
    odds = item.get("odds") or {}
    bookmakers = item.get("bookmakers") or {}

    odds_bookmakers = sorted(list(odds.keys()))
    if not odds_bookmakers:
        odds_bookmakers = sorted(list(bookmakers.keys()))

    dto = NormalizedFixture(
        fixture_id=item.get("fixtureId"),
        sport_id=sport.get("sportId"),
        sport_name=sport.get("sportName"),
        league_id=tournament.get("tournamentId"),
        league_name=tournament.get("tournamentName"),
        category_name=tournament.get("categoryName"),
        home=participants.get("participant1Name"),
        away=participants.get("participant2Name"),
        live=status.get("live"),
        status_id=status.get("statusId"),
        status_name=status.get("statusName"),
        participant1_abbr=participants.get("participant1Abbr"),
        participant2_abbr=participants.get("participant2Abbr"),
        odds_bookmakers=odds_bookmakers,
        raw=item,
    )
    return asdict(dto)

if __name__ == "__main__":
    print("SCRIPT OK")
