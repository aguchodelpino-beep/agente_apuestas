from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass(slots=True)
class ProviderRef:
    provider: str
    provider_event_id: str
    raw_home_team: str = ""
    raw_away_team: str = ""
    raw_league: str = ""
    raw_start_time: str = ""
    confidence: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class EnrichedEvent:
    internal_event_id: str
    sport: str
    league: str
    start_time: str
    home_team: str
    away_team: str
    teams: list[str] = field(default_factory=list)
    bookmakers: list[dict[str, Any]] = field(default_factory=list)
    markets: list[dict[str, Any]] = field(default_factory=list)
    closing_odds: list[dict[str, Any]] = field(default_factory=list)
    sharp_odds: list[dict[str, Any]] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)
    injuries: list[dict[str, Any]] = field(default_factory=list)
    surface: str | None = None
    weather: dict[str, Any] = field(default_factory=dict)
    line_movement: list[dict[str, Any]] = field(default_factory=list)
    provider_map: dict[str, dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if not data["teams"]:
            data["teams"] = [self.home_team, self.away_team]
        return data


def build_enriched_event(
    *,
    internal_event_id: str,
    sport: str,
    league: str,
    start_time: str,
    home_team: str,
    away_team: str,
    provider_refs: list[ProviderRef] | None = None,
    **extra: Any,
) -> EnrichedEvent:
    provider_map: dict[str, dict[str, Any]] = {}
    for ref in provider_refs or []:
        provider_map[ref.provider] = ref.to_dict()

    event = EnrichedEvent(
        internal_event_id=internal_event_id,
        sport=sport,
        league=league,
        start_time=start_time,
        home_team=home_team,
        away_team=away_team,
        teams=[home_team, away_team],
        provider_map=provider_map,
        bookmakers=extra.get("bookmakers", []),
        markets=extra.get("markets", []),
        closing_odds=extra.get("closing_odds", []),
        sharp_odds=extra.get("sharp_odds", []),
        stats=extra.get("stats", {}),
        injuries=extra.get("injuries", []),
        surface=extra.get("surface"),
        weather=extra.get("weather", {}),
        line_movement=extra.get("line_movement", []),
    )
    return event

if __name__ == "__main__":
    print("SCRIPT OK")
