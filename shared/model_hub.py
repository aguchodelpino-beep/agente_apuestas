"""
Hub de integración para Fase 3.
Orquesta modelos por deporte sin tocar aún los services existentes.
SCRIPT_OK
"""
from __future__ import annotations

from typing import Any, Optional

from departments.deportes.futbol.poisson_model import poisson_match_probs, xg_from_event
from departments.deportes.tenis.elo_model import EloStore, win_probability
from departments.deportes.basket.ratings_model import ratings_from_event, project_scores
from shared.monte_carlo import run_football_monte_carlo, run_basketball_monte_carlo
from shared.ensemble_engine import ModelOutput, weighted_ensemble, get_sport_weights
from shared.market_models import build_market_probs


def _safe_odds(event: dict) -> dict:
    odds = event.get("odds") or {}
    return odds if isinstance(odds, dict) else {}


def _normalize_event(event: dict) -> dict:
    """
    Adapta el formato real del cache/fixture al shape que esperan los modelos.
    No muta el original.
    """
    ev = dict(event)

    # ── xG: aliases home_xg/away_xg → xg_home/xg_away ──────────────────────
    if ev.get("home_xg") is not None and "xg_home" not in ev:
        ev["xg_home"] = ev["home_xg"]
    if ev.get("away_xg") is not None and "xg_away" not in ev:
        ev["xg_away"] = ev["away_xg"]

    # ── odds: extraer desde markets[h2h] si no hay ev["odds"] ────────────────
    if not ev.get("odds"):
        markets = ev.get("markets") or []
        h2h = next((m for m in markets if m.get("key") in ("h2h", "match_winner")), None)
        if h2h:
            outcomes = h2h.get("outcomes") or []
            odds_dict: dict = {}
            for o in outcomes:
                name = str(o.get("name") or "").lower()
                price = o.get("price")
                if price is None:
                    continue
                if name in ("1", "home"):
                    odds_dict["home"] = float(price)
                    odds_dict["1"]    = float(price)
                elif name in ("x", "draw"):
                    odds_dict["draw"] = float(price)
                    odds_dict["x"]    = float(price)
                elif name in ("2", "away"):
                    odds_dict["away"] = float(price)
                    odds_dict["2"]    = float(price)
            if odds_dict:
                ev["odds"] = odds_dict

    # ── tenis: aliases home/away → home_team/away_team, player_a/player_b ───
    if not ev.get("home_team") and ev.get("home"):
        ev["home_team"] = ev["home"]
        ev["player_a"]  = ev["home"]
    if not ev.get("away_team") and ev.get("away"):
        ev["away_team"] = ev["away"]
        ev["player_b"]  = ev["away"]

    # ── basket: stats inline → stats dict ────────────────────────────────────
    if not ev.get("stats"):
        stats: dict = {}
        for prefix in ("home", "away"):
            for key in ("ortg", "drtg", "pace", "offensive_rating", "defensive_rating"):
                full = f"{prefix}_{key}"
                if ev.get(full) is not None:
                    stats[full] = ev[full]
        if stats:
            ev["stats"] = stats

    return ev


def build_futbol_snapshot(event: dict) -> Optional[dict[str, Any]]:
    event = _normalize_event(event)
    xg = xg_from_event(event)
    if not xg:
        return None

    home_xg, away_xg = xg
    poisson = poisson_match_probs(home_xg, away_xg)
    mc = run_football_monte_carlo(home_xg, away_xg, n_sims=5000, seed=42)

    ensemble = weighted_ensemble(
        [
            ModelOutput("poisson", poisson.home_win, poisson.draw, poisson.away_win, confidence=1.0),
            ModelOutput("monte_carlo", mc.home_win_pct, mc.draw_pct, mc.away_win_pct, confidence=0.9),
        ],
        custom_weights=get_sport_weights("futbol"),
    )

    market_probs = build_market_probs(
        home_win_prob=ensemble.prob_home,
        draw_prob=ensemble.prob_draw,
        away_win_prob=ensemble.prob_away,
        projected_total=mc.mean_total_goals,
        market_odds=_safe_odds(event),
        total_line=event.get("total_line"),
        sport="futbol",
    )

    return {
        "sport": "futbol",
        "inputs": {"home_xg": home_xg, "away_xg": away_xg},
        "poisson": {
            "home_win": poisson.home_win,
            "draw": poisson.draw,
            "away_win": poisson.away_win,
            "over_2_5": poisson.over_2_5,
            "btts_yes": poisson.btts_yes,
        },
        "monte_carlo": {
            "home_win_pct": mc.home_win_pct,
            "draw_pct": mc.draw_pct,
            "away_win_pct": mc.away_win_pct,
            "mean_total_goals": mc.mean_total_goals,
        },
        "ensemble": {
            "prob_home": ensemble.prob_home,
            "prob_draw": ensemble.prob_draw,
            "prob_away": ensemble.prob_away,
        },
        "market_probs": [m.__dict__ for m in market_probs],
    }


def build_tenis_snapshot(
    event: dict,
    store: Optional[EloStore] = None,
) -> Optional[dict[str, Any]]:
    event = _normalize_event(event)
    player_a = event.get("home_team") or event.get("player_a") or event.get("player1")
    player_b = event.get("away_team") or event.get("player_b") or event.get("player2")
    surface = event.get("surface")

    if not player_a or not player_b:
        return None

    store = store or EloStore()
    prob_a, prob_b = win_probability(store, str(player_a), str(player_b), surface=surface)

    ensemble = weighted_ensemble(
        [
            ModelOutput("elo_surface", prob_a, 0.0, prob_b, confidence=1.0),
        ],
        custom_weights=get_sport_weights("tenis"),
    )

    market_probs = build_market_probs(
        home_win_prob=ensemble.prob_home,
        draw_prob=0.0,
        away_win_prob=ensemble.prob_away,
        projected_total=0.0,
        market_odds=_safe_odds(event),
        sport="tenis",
    )

    return {
        "sport": "tenis",
        "inputs": {"player_a": player_a, "player_b": player_b, "surface": surface},
        "elo": {
            "prob_a": prob_a,
            "prob_b": prob_b,
        },
        "ensemble": {
            "prob_home": ensemble.prob_home,
            "prob_draw": ensemble.prob_draw,
            "prob_away": ensemble.prob_away,
        },
        "market_probs": [m.__dict__ for m in market_probs],
    }


def build_basket_snapshot(event: dict) -> Optional[dict[str, Any]]:
    event = _normalize_event(event)
    ratings = ratings_from_event(event)
    if not ratings:
        return None

    home, away = ratings
    proj = project_scores(home, away)
    mc = run_basketball_monte_carlo(
        home_win_prob=proj.home_win_prob,
        projected_total=proj.projected_total,
        spread=float(event.get("spread", 0.0)),
        n_sims=5000,
        seed=42,
    )

    ensemble = weighted_ensemble(
        [
            ModelOutput("net_rating", proj.home_win_prob, 0.0, proj.away_win_prob, confidence=1.0),
            ModelOutput("monte_carlo", mc["home_win_pct"], 0.0, mc["away_win_pct"], confidence=0.9),
        ],
        custom_weights=get_sport_weights("basket"),
    )

    market_probs = build_market_probs(
        home_win_prob=ensemble.prob_home,
        draw_prob=0.0,
        away_win_prob=ensemble.prob_away,
        projected_total=proj.projected_total,
        market_odds=_safe_odds(event),
        spread=event.get("spread"),
        total_line=event.get("total_line"),
        sport="basket",
    )

    return {
        "sport": "basket",
        "inputs": {
            "home_team": home.team,
            "away_team": away.team,
        },
        "ratings": {
            "home_win_prob": proj.home_win_prob,
            "away_win_prob": proj.away_win_prob,
            "projected_total": proj.projected_total,
            "home_projected_score": proj.home_projected_score,
            "away_projected_score": proj.away_projected_score,
        },
        "monte_carlo": mc,
        "ensemble": {
            "prob_home": ensemble.prob_home,
            "prob_draw": ensemble.prob_draw,
            "prob_away": ensemble.prob_away,
        },
        "market_probs": [m.__dict__ for m in market_probs],
    }


def build_model_snapshot(sport: str, event: dict, **kwargs) -> Optional[dict[str, Any]]:
    sport = (sport or "").lower().strip()
    if sport == "futbol":
        return build_futbol_snapshot(event)
    if sport == "tenis":
        return build_tenis_snapshot(event, **kwargs)
    if sport == "basket":
        return build_basket_snapshot(event)
    return None

if __name__ == "__main__":
    print("SCRIPT OK")
