"""
Motor de simulación Monte Carlo para partidos.
Entrega distribuciones, no solo picks puntuales.
SCRIPT_OK
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field


@dataclass
class SimResult:
    n_sims: int
    home_win_pct: float
    draw_pct: float
    away_win_pct: float
    over_2_5_pct: float
    mean_total_goals: float
    percentile_5_total: float
    percentile_95_total: float
    raw_totals: list[float] = field(default_factory=list, repr=False)


def _sample_poisson(lam: float) -> int:
    if lam <= 0:
        return 0
    limit = math.exp(-lam)
    k = 0
    p = 1.0
    while p > limit:
        k += 1
        p *= random.random()
    return k - 1


def run_football_monte_carlo(
    home_xg: float,
    away_xg: float,
    n_sims: int = 10000,
    seed: int | None = None,
) -> SimResult:
    if seed is not None:
        random.seed(seed)

    home_wins = 0
    draws = 0
    away_wins = 0
    overs = 0
    totals: list[float] = []

    for _ in range(n_sims):
        h = _sample_poisson(home_xg)
        a = _sample_poisson(away_xg)
        total = h + a
        totals.append(float(total))

        if h > a:
            home_wins += 1
        elif h == a:
            draws += 1
        else:
            away_wins += 1

        if total >= 3:
            overs += 1

    totals_sorted = sorted(totals)
    p5_idx = max(0, int(0.05 * n_sims) - 1)
    p95_idx = min(n_sims - 1, int(0.95 * n_sims))

    return SimResult(
        n_sims=n_sims,
        home_win_pct=round(home_wins / n_sims, 4),
        draw_pct=round(draws / n_sims, 4),
        away_win_pct=round(away_wins / n_sims, 4),
        over_2_5_pct=round(overs / n_sims, 4),
        mean_total_goals=round(sum(totals) / n_sims, 3),
        percentile_5_total=totals_sorted[p5_idx],
        percentile_95_total=totals_sorted[p95_idx],
        raw_totals=[],
    )


def run_basketball_monte_carlo(
    home_win_prob: float,
    projected_total: float,
    spread: float = 0.0,
    n_sims: int = 10000,
    seed: int | None = None,
) -> dict:
    if seed is not None:
        random.seed(seed)

    std_total = 12.0
    std_margin = 11.0

    margin_mean = max(-20.0, min(20.0, (home_win_prob - 0.5) * 24.0 + spread))

    home_wins = 0
    overs = 0
    covers = 0

    for _ in range(n_sims):
        sampled_total = random.gauss(projected_total, std_total)
        sampled_margin = random.gauss(margin_mean, std_margin)

        if sampled_margin > 0:
            home_wins += 1
        if sampled_total > projected_total:
            overs += 1
        if sampled_margin > spread:
            covers += 1

    home_win_pct = home_wins / n_sims
    over_pct = overs / n_sims
    cover_pct = covers / n_sims

    return {
        "n_sims": n_sims,
        "home_win_pct": round(home_win_pct, 4),
        "away_win_pct": round(1.0 - home_win_pct, 4),
        "over_pct": round(over_pct, 4),
        "under_pct": round(1.0 - over_pct, 4),
        "ats_cover_pct": round(cover_pct, 4),
    }

if __name__ == "__main__":
    print("SCRIPT OK")
