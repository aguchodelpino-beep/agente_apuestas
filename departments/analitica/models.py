from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BetOpportunity:
    internal_event_id: str
    sport: str
    league: str
    market_key: str
    selection_name: str
    odds_taken: float
    model_prob: float
    bankroll: float
    bookmaker_key: str = "pinnacle"
    model_name: str = "unknown_model"
    model_version: str = "v1"
    event_start_time: str | None = None

    def __post_init__(self) -> None:
        if not self.internal_event_id.strip():
            raise ValueError("internal_event_id requerido")
        if self.odds_taken <= 1.0:
            raise ValueError("odds_taken debe ser > 1.0")
        if not (0.0 <= self.model_prob <= 1.0):
            raise ValueError("model_prob debe estar entre 0 y 1")
        if self.bankroll < 0:
            raise ValueError("bankroll no puede ser negativo")


@dataclass(frozen=True)
class KellyConfig:
    fractional_kelly: float = 0.25
    max_stake_pct: float = 0.02
    min_edge_pct: float = 0.0
    min_ev_pct: float = 0.0
    unit_size: float = 1.0

    def __post_init__(self) -> None:
        if not (0.0 < self.fractional_kelly <= 1.0):
            raise ValueError("fractional_kelly debe estar en (0, 1]")
        if self.max_stake_pct < 0:
            raise ValueError("max_stake_pct no puede ser negativo")
        if self.unit_size <= 0:
            raise ValueError("unit_size debe ser > 0")


@dataclass(frozen=True)
class KellyDecision:
    implied_prob: float
    edge_pct: float
    ev_pct: float
    full_kelly_pct: float
    fractional_kelly_pct: float
    capped_stake_pct: float
    recommended_stake: float
    recommended_units: float
    should_bet: bool
    reason: str
