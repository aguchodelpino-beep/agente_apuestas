"""
Modelo de Distribución de Poisson para fútbol.
Estima P(1X2), totals y BTTS a partir de goles esperados (xG).
SCRIPT_OK
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class PoissonResult:
    home_win: float
    draw: float
    away_win: float
    over_2_5: float
    under_2_5: float
    btts_yes: float
    btts_no: float
    home_xg: float
    away_xg: float


def _poisson_pmf(k: int, lam: float) -> float:
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    return (lam ** k) * math.exp(-lam) / math.factorial(k)


def poisson_match_probs(
    home_xg: float,
    away_xg: float,
    max_goals: int = 10,
) -> PoissonResult:
    home_win = 0.0
    draw = 0.0
    away_win = 0.0
    over_2_5 = 0.0
    btts_both = 0.0

    for h in range(max_goals + 1):
        ph = _poisson_pmf(h, home_xg)
        for a in range(max_goals + 1):
            pa = _poisson_pmf(a, away_xg)
            p = ph * pa

            if h > a:
                home_win += p
            elif h == a:
                draw += p
            else:
                away_win += p

            if h + a >= 3:
                over_2_5 += p

            if h >= 1 and a >= 1:
                btts_both += p

    total_1x2 = home_win + draw + away_win
    if total_1x2 > 0:
        home_win /= total_1x2
        draw /= total_1x2
        away_win /= total_1x2

    return PoissonResult(
        home_win=round(home_win, 4),
        draw=round(draw, 4),
        away_win=round(away_win, 4),
        over_2_5=round(over_2_5, 4),
        under_2_5=round(1.0 - over_2_5, 4),
        btts_yes=round(btts_both, 4),
        btts_no=round(1.0 - btts_both, 4),
        home_xg=round(float(home_xg), 3),
        away_xg=round(float(away_xg), 3),
    )


def xg_from_event(event: dict) -> Optional[tuple[float, float]]:
    stats = event.get("stats", {})

    xg_home = event.get("xg_home", stats.get("xg_home"))
    xg_away = event.get("xg_away", stats.get("xg_away"))
    if xg_home is not None and xg_away is not None:
        return float(xg_home), float(xg_away)

    odds = event.get("odds", {})
    h_odds = odds.get("home") or odds.get("1")
    a_odds = odds.get("away") or odds.get("2")
    if not h_odds or not a_odds:
        return None

    try:
        ph = 1.0 / float(h_odds)
        pa = 1.0 / float(a_odds)
    except (ValueError, ZeroDivisionError):
        return None

    home_xg = 1.4 * (ph / 0.45)
    away_xg = 1.1 * (pa / 0.35)

    home_xg = round(min(max(home_xg, 0.2), 4.0), 2)
    away_xg = round(min(max(away_xg, 0.2), 4.0), 2)
    return home_xg, away_xg

if __name__ == "__main__":
    print("SCRIPT OK")
