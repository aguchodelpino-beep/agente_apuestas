"""
Enriquecedor de picks con snapshots de modelos.
Capa segura previa al wiring directo en services.
SCRIPT_OK
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from shared.model_hub import build_model_snapshot


SPORT_ALIASES = {
    "futbol": "futbol",
    "football": "futbol",
    "soccer": "futbol",
    "tenis": "tenis",
    "tennis": "tenis",
    "basket": "basket",
    "basketball": "basket",
    "nba": "basket",
}


def normalize_sport_name(sport: str | None) -> str:
    key = (sport or "").strip().lower()
    return SPORT_ALIASES.get(key, key)


def enrich_pick_with_models(pick: dict[str, Any], sport: str) -> dict[str, Any]:
    out = deepcopy(pick)
    norm_sport = normalize_sport_name(sport)

    event = out.get("event") or out.get("fixture") or out.get("match") or {}
    if not isinstance(event, dict):
        event = {}

    try:
        snapshot = build_model_snapshot(norm_sport, event)
    except Exception:
        snapshot = None

    if snapshot:
        out["model_snapshot"] = snapshot
        ensemble = snapshot.get("ensemble") or {}
        out["model_probs"] = {
            "home": ensemble.get("prob_home"),
            "draw": ensemble.get("prob_draw"),
            "away": ensemble.get("prob_away"),
        }

        market_probs = snapshot.get("market_probs") or []
        best_edge = None
        best_market = None
        for mp in market_probs:
            if not isinstance(mp, dict):
                continue
            edge = mp.get("edge")
            if isinstance(edge, (int, float)) and (best_edge is None or edge > best_edge):
                best_edge = float(edge)
                best_market = mp.get("market")

        if best_edge is not None:
            out["best_model_edge"] = round(best_edge, 4)
        if best_market:
            out["best_model_market"] = best_market

    return out


def enrich_picks_with_models(picks: list[dict[str, Any]], sport: str) -> list[dict[str, Any]]:
    return [enrich_pick_with_models(pick, sport) for pick in picks]

if __name__ == "__main__":
    print("SCRIPT OK")
