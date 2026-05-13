from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Fixture:
    fixture_id: str
    home: str
    away: str
    league: str = ""
    status: str = ""
    live: bool = False
    start_time: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class OddsMarket:
    fixture_id: str
    market: str
    home_odds: float = 0.0
    away_odds: float = 0.0
    bookmaker: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class PickCandidate:
    fixture_id: str
    sport: str
    league: str
    home: str
    away: str
    market: str
    selection: str
    odds: float
    model_prob: float = 0.0
    edge: float = 0.0
    confidence: float = 0.0
    raw: dict[str, Any] = field(default_factory=dict)

if __name__ == "__main__":
    print("SCRIPT OK")
