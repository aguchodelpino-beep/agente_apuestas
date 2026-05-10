from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


def _safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def calculate_clv_pct_decimal(opening: float | None, closing: float | None) -> Optional[float]:
    if opening is None or closing is None or opening == 0:
        return None
    return round(((closing - opening) / opening) * 100.0, 6)


def calculate_point_movement(opening_point: float | None, closing_point: float | None) -> Optional[float]:
    if opening_point is None or closing_point is None:
        return None
    return closing_point - opening_point


@dataclass
class PickContext:
    opening_odds: Optional[float] = None
    closing_odds: Optional[float] = None
    clv_pct: Optional[float] = None
    point_movement: Optional[float] = None

    def describe(self) -> str:
        if self.opening_odds is None or self.closing_odds is None:
            return "sin CLV"
        if self.closing_odds > self.opening_odds:
            move = f"subió de {self.opening_odds:.2f} → {self.closing_odds:.2f}"
        elif self.closing_odds < self.opening_odds:
            move = f"bajó de {self.opening_odds:.2f} → {self.closing_odds:.2f}"
        else:
            move = f"cerró igual en {self.closing_odds:.2f}"
        clv_txt = "N/A" if self.clv_pct is None else f"{self.clv_pct:+.2f}%"
        return f"CLV {clv_txt} | {move}"


def enrich_pick_with_clv(
    opening_odds: float | None,
    closing_odds: float | None,
    opening_point: float | None = None,
    closing_point: float | None = None,
) -> PickContext:
    return PickContext(
        opening_odds=_safe_float(opening_odds),
        closing_odds=_safe_float(closing_odds),
        clv_pct=calculate_clv_pct_decimal(_safe_float(opening_odds), _safe_float(closing_odds)),
        point_movement=calculate_point_movement(_safe_float(opening_point), _safe_float(closing_point)),
    )
