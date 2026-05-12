from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class CapViolation:
    reason: str
    limit_pct: float
    used_pct: float
    stake_pct: float

    def __str__(self) -> str:
        return (
            f"CapViolation({self.reason}: "
            f"usado={self.used_pct}% + stake={self.stake_pct}% "
            f"> limite={self.limit_pct}%)"
        )


@dataclass
class CapLimits:
    max_daily_pct: float = 5.0
    max_per_event_pct: float = 2.0
    max_per_league_pct: float = 3.0

    def check(
        self,
        stake_pct: float,
        daily_used_pct: float = 0.0,
        event_used_pct: float = 0.0,
        league_used_pct: float = 0.0,
    ) -> Optional[CapViolation]:
        if daily_used_pct + stake_pct > self.max_daily_pct:
            return CapViolation(
                reason="daily_cap",
                limit_pct=self.max_daily_pct,
                used_pct=daily_used_pct,
                stake_pct=stake_pct,
            )
        if event_used_pct + stake_pct > self.max_per_event_pct:
            return CapViolation(
                reason="event_cap",
                limit_pct=self.max_per_event_pct,
                used_pct=event_used_pct,
                stake_pct=stake_pct,
            )
        if league_used_pct + stake_pct > self.max_per_league_pct:
            return CapViolation(
                reason="league_cap",
                limit_pct=self.max_per_league_pct,
                used_pct=league_used_pct,
                stake_pct=stake_pct,
            )
        return None

    def clamp_stake_pct(
        self,
        stake_pct: float,
        daily_used_pct: float = 0.0,
        event_used_pct: float = 0.0,
        league_used_pct: float = 0.0,
    ) -> float:
        max_by_daily = self.max_daily_pct - daily_used_pct
        max_by_event = self.max_per_event_pct - event_used_pct
        max_by_league = self.max_per_league_pct - league_used_pct
        allowed = min(stake_pct, max_by_daily, max_by_event, max_by_league)
        return round(max(allowed, 0.0), 4)
