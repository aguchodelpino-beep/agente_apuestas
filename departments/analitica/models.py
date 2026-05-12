from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class BetOpportunity:
    internal_event_id: str
    sport: str
    league: str
    market_key: str
    selection_name: str
    odds_taken: float
    model_prob: float
    bankroll: float
    model_name: str = "default"
    model_version: Optional[str] = None
    event_start_time: Optional[str] = None
    event_title: Optional[str] = None

    def __post_init__(self):
        if not (0.0 < self.model_prob < 1.0):
            raise ValueError(
                f"model_prob debe estar entre 0 y 1 exclusivo, recibido: {self.model_prob}"
            )


@dataclass
class KellyConfig:
    fractional_kelly: float = 0.25
    max_stake_pct: float = 0.05
    min_edge_pct: float = 0.0
    min_ev_pct: float = 0.0
    unit_size: float = 10.0


@dataclass
class KellyDecision:
    should_bet: bool
    full_kelly_pct: float
    fractional_kelly_pct: float
    capped_stake_pct: float
    recommended_stake: float
    recommended_units: float
    ev_pct: float
    reason: str
    # campos extendidos con default para retrocompatibilidad
    implied_prob: float = 0.0
    edge_pct: float = 0.0
    stake_units: float = 0.0
