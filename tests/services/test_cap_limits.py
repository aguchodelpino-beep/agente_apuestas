from __future__ import annotations
import pytest
from departments.analitica.cap_limits import CapLimits, CapViolation


def test_no_violation_within_limits():
    caps = CapLimits(max_daily_pct=5.0, max_per_event_pct=2.0, max_per_league_pct=3.0)
    result = caps.check(
        stake_pct=1.5,
        daily_used_pct=2.0,
        event_used_pct=0.0,
        league_used_pct=1.0,
    )
    assert result is None


def test_daily_cap_violation():
    caps = CapLimits(max_daily_pct=5.0, max_per_event_pct=2.0, max_per_league_pct=3.0)
    result = caps.check(
        stake_pct=2.0,
        daily_used_pct=4.5,
        event_used_pct=0.0,
        league_used_pct=0.0,
    )
    assert isinstance(result, CapViolation)
    assert result.reason == "daily_cap"


def test_event_cap_violation():
    caps = CapLimits(max_daily_pct=5.0, max_per_event_pct=2.0, max_per_league_pct=3.0)
    result = caps.check(
        stake_pct=1.0,
        daily_used_pct=0.0,
        event_used_pct=1.5,
        league_used_pct=0.0,
    )
    assert isinstance(result, CapViolation)
    assert result.reason == "event_cap"


def test_league_cap_violation():
    caps = CapLimits(max_daily_pct=5.0, max_per_event_pct=2.0, max_per_league_pct=3.0)
    result = caps.check(
        stake_pct=1.0,
        daily_used_pct=0.0,
        event_used_pct=0.0,
        league_used_pct=2.5,
    )
    assert isinstance(result, CapViolation)
    assert result.reason == "league_cap"


def test_cap_clamp_returns_max_allowed():
    caps = CapLimits(max_daily_pct=5.0, max_per_event_pct=2.0, max_per_league_pct=3.0)
    clamped = caps.clamp_stake_pct(
        stake_pct=3.0,
        daily_used_pct=4.0,
        event_used_pct=0.0,
        league_used_pct=0.0,
    )
    assert clamped == 1.0
