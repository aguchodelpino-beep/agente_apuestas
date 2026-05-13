"""
Motor de ratings para basket: Offensive Rating, Defensive Rating, Net Rating y Pace.
SCRIPT_OK
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional


LEAGUE_AVG_ORTG = 114.0
LEAGUE_AVG_PACE = 99.5


@dataclass
class TeamRatings:
    team: str
    ortg: float
    drtg: float
    pace: float
    net_rtg: float = 0.0

    def __post_init__(self) -> None:
        self.net_rtg = round(float(self.ortg) - float(self.drtg), 2)


@dataclass
class BasketMatchupResult:
    home_win_prob: float
    away_win_prob: float
    projected_total: float
    home_projected_score: float
    away_projected_score: float


def project_scores(home: TeamRatings, away: TeamRatings) -> BasketMatchupResult:
    avg_pace = (float(home.pace) + float(away.pace)) / 2.0

    home_pts = (float(home.ortg) * (float(away.drtg) / LEAGUE_AVG_ORTG)) * (avg_pace / 100.0)
    away_pts = (float(away.ortg) * (float(home.drtg) / LEAGUE_AVG_ORTG)) * (avg_pace / 100.0)

    net_diff = float(home.net_rtg) - float(away.net_rtg)
    home_win_prob = 1.0 / (1.0 + math.exp(-net_diff / 7.0))
    away_win_prob = 1.0 - home_win_prob

    return BasketMatchupResult(
        home_win_prob=round(home_win_prob, 4),
        away_win_prob=round(away_win_prob, 4),
        projected_total=round(home_pts + away_pts, 1),
        home_projected_score=round(home_pts, 1),
        away_projected_score=round(away_pts, 1),
    )


def ratings_from_event(event: dict) -> Optional[tuple[TeamRatings, TeamRatings]]:
    stats = event.get("stats", {})

    def _extract(prefix: str, team_name: str) -> Optional[TeamRatings]:
        ortg = stats.get(f"{prefix}_ortg") or stats.get(f"{prefix}_offensive_rating")
        drtg = stats.get(f"{prefix}_drtg") or stats.get(f"{prefix}_defensive_rating")
        pace = stats.get(f"{prefix}_pace")
        if ortg is None or drtg is None or pace is None:
            return None
        return TeamRatings(
            team=team_name,
            ortg=float(ortg),
            drtg=float(drtg),
            pace=float(pace),
        )

    home_name = event.get("home_team", "Home")
    away_name = event.get("away_team", "Away")

    home = _extract("home", home_name)
    away = _extract("away", away_name)
    if home and away:
        return home, away

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

    h_net = 10.0 * (ph - 0.5)
    a_net = 10.0 * (pa - 0.5)

    home = TeamRatings(
        team=home_name,
        ortg=LEAGUE_AVG_ORTG + h_net / 2.0,
        drtg=LEAGUE_AVG_ORTG - h_net / 2.0,
        pace=LEAGUE_AVG_PACE,
    )
    away = TeamRatings(
        team=away_name,
        ortg=LEAGUE_AVG_ORTG + a_net / 2.0,
        drtg=LEAGUE_AVG_ORTG - a_net / 2.0,
        pace=LEAGUE_AVG_PACE,
    )
    return home, away

if __name__ == "__main__":
    print("SCRIPT OK")
