"""
Extrae probabilidades fair (sin margen de bookmaker) a partir de odds 1X2.
Usado como model_prob en fútbol cuando no hay modelo Poisson con histórico.
"""
from __future__ import annotations
from typing import Optional


def fair_probs_1x2(
    odds_home: float,
    odds_draw: float,
    odds_away: float,
) -> dict[str, float]:
    """
    Remueve el overround y retorna probabilidades fair normalizadas.

    Returns:
        {"home": float, "draw": float, "away": float, "overround": float}
    """
    if any(o <= 1.0 for o in (odds_home, odds_draw, odds_away)):
        raise ValueError("Todas las odds deben ser > 1.0")

    raw_home = 1.0 / odds_home
    raw_draw = 1.0 / odds_draw
    raw_away = 1.0 / odds_away
    overround = raw_home + raw_draw + raw_away

    return {
        "home":      round(raw_home / overround, 6),
        "draw":      round(raw_draw / overround, 6),
        "away":      round(raw_away / overround, 6),
        "overround": round(overround, 6),
    }


def model_prob_home(
    odds_home: float,
    odds_draw: float,
    odds_away: float,
    edge_boost: float = 0.0,
) -> float:
    """
    Retorna la probabilidad fair del home + edge_boost opcional.
    edge_boost: descuento de margen propio (ej. 0.01 = 1% de ventaja de info)
    """
    probs = fair_probs_1x2(odds_home, odds_draw, odds_away)
    return min(probs["home"] + edge_boost, 0.95)


def extract_odds_1x2(fixture: dict) -> Optional[tuple[float, float, float]]:
    """
    Extrae (odds_home, odds_draw, odds_away) del fixture de cachefutbol.
    Soporta formato {'TeamA': 2.10, 'Draw': 3.40, 'TeamB': 3.20}.
    Retorna None si faltan datos.
    """
    odds = fixture.get("odds")
    if not odds or not isinstance(odds, dict):
        return None

    home_team = (fixture.get("home_team") or fixture.get("home") or "").strip()
    away_team = (fixture.get("away_team") or fixture.get("away") or "").strip()

    # Buscar Draw explícito
    draw_val = odds.get("Draw") or odds.get("draw") or odds.get("Empate")
    if not draw_val:
        return None

    # Buscar home por nombre exacto, luego por posición
    home_val = odds.get(home_team)
    away_val = odds.get(away_team)

    # Fallback: primer y último valor no-Draw
    if not home_val or not away_val:
        non_draw = [(k, v) for k, v in odds.items()
                    if k.lower() not in ("draw", "empate")]
        if len(non_draw) >= 2:
            home_val = home_val or non_draw[0][1]
            away_val = away_val or non_draw[-1][1]

    if not home_val or not away_val or not draw_val:
        return None

    try:
        return float(home_val), float(draw_val), float(away_val)
    except (TypeError, ValueError):
        return None

if __name__ == "__main__":
    print("SCRIPT OK")
