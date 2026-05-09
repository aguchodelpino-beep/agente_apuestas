from __future__ import annotations

from typing import Any

SPORTS = {"futbol", "tenis", "basket"}
MARKETS = {"1x2", "moneyline", "over_under", "spreads", "totals", "winner"}


def is_non_empty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def normalize_sport(value: Any) -> str | None:
    if not is_non_empty_str(value):
        return None
    sport = value.strip().lower()
    return sport if sport in SPORTS else None


def is_valid_fixture_id(value: Any) -> bool:
    return is_non_empty_str(value) and len(value.strip()) >= 6


def is_valid_market(value: Any) -> bool:
    if not is_non_empty_str(value):
        return False
    return value.strip().lower() in MARKETS


def is_valid_price(value: Any) -> bool:
    try:
        price = float(value)
        return price > 1.0
    except (TypeError, ValueError):
        return False


def clamp(value: float, low: float, high: float) -> float:
    if value < low:
        return low
    if value > high:
        return high
    return value


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def has_items(value: Any) -> bool:
    return isinstance(value, (list, tuple, set, dict)) and len(value) > 0
