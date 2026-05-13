"""
Modelos por mercado: moneyline, spreads y totals.
Traduce probabilidades de partido a mercados específicos.
SCRIPT_OK
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import NormalDist
from typing import Optional


@dataclass
class MarketProb:
    market: str
    prob: float
    fair_odds: float
    edge: float = 0.0
    model_source: str = ""


def prob_to_fair_odds(prob: float) -> float:
    if prob <= 0:
        return 9999.0
    return round(1.0 / prob, 3)


def spread_prob(
    home_win_prob: float,
    spread_points: float,
    std_dev: float = 12.0,
) -> tuple[float, float]:
    home_win_prob = max(0.01, min(0.99, float(home_win_prob)))
    std_dev = max(0.1, float(std_dev))

    nd = NormalDist()
    mu_margin = nd.inv_cdf(home_win_prob) * std_dev
    cover_home = 1.0 - NormalDist(mu=mu_margin, sigma=std_dev).cdf(float(spread_points))
    cover_home = max(0.01, min(0.99, cover_home))

    return round(cover_home, 4), round(1.0 - cover_home, 4)


def total_prob(
    projected_total: float,
    line: float,
    std_dev: float = 7.0,
) -> tuple[float, float]:
    z = (line - projected_total) / std_dev
    prob_under = 0.5 * math.erfc(-z / math.sqrt(2))
    prob_over = 1.0 - prob_under
    return round(prob_over, 4), round(prob_under, 4)


def build_market_probs(
    home_win_prob: float,
    draw_prob: float,
    away_win_prob: float,
    projected_total: float,
    market_odds: dict,
    spread: Optional[float] = None,
    total_line: Optional[float] = None,
    sport: str = "futbol",
) -> list[MarketProb]:
    results: list[MarketProb] = []

    def _add(market: str, model_prob: float, odds_key: str) -> None:
        fair = prob_to_fair_odds(model_prob)
        mkt_odds = market_odds.get(odds_key)
        edge = 0.0
        if mkt_odds:
            try:
                implied = 1.0 / float(mkt_odds)
                edge = round(model_prob - implied, 4)
            except (ValueError, ZeroDivisionError):
                edge = 0.0
        results.append(
            MarketProb(
                market=market,
                prob=round(model_prob, 4),
                fair_odds=fair,
                edge=edge,
                model_source="market_models",
            )
        )

    _add("moneyline_home", home_win_prob, "home")
    if sport == "futbol":
        _add("moneyline_draw", draw_prob, "draw")
    _add("moneyline_away", away_win_prob, "away")

    if total_line is not None:
        over_p, under_p = total_prob(projected_total, total_line)
        _add("total_over", over_p, "over")
        _add("total_under", under_p, "under")

    if spread is not None:
        cover_h, cover_a = spread_prob(home_win_prob, spread)
        _add("spread_home", cover_h, "spread_home")
        _add("spread_away", cover_a, "spread_away")

    return results

if __name__ == "__main__":
    print("SCRIPT OK")
