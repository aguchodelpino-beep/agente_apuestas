from __future__ import annotations

from typing import Any

from departments.deportes.basket_repo import list_live_fixtures
from departments.analitica.models import KellyDecision
from departments.analitica.kelly_service import evaluate_kelly


def _row_title(row: dict[str, Any]) -> str:
    home = row.get("home") or row.get("home_team") or row.get("player1") or "TBD"
    away = row.get("away") or row.get("away_team") or row.get("player2") or "TBD"
    return f"{home} vs {away}"


def _row_tour(row: dict[str, Any]) -> str:
    league = row.get("league")
    if isinstance(league, str) and league.strip():
        return league.strip()
    return "Basket"


def _markets_count(row: dict[str, Any]) -> int:
    markets = row.get("markets", [])
    return len(markets) if isinstance(markets, list) else 0


def record_bet(payload: dict[str, Any]) -> None:
    pass


def build_basket_pick_messages(
    bankroll: float = 1000.0,
    model_name: str = "poisson_match_v1",
    model_version: str = "2026.05",
) -> list[str]:
    rows = list_live_fixtures()
    if not rows:
        return ["🏀 BASKET PICKS", "", "Sin partidos en vivo ahora."]

    lines: list[str] = ["🏀 BASKET PICKS", ""]
    picks_found = 0

    for row in rows:
        markets = row.get("markets", [])
        if not isinstance(markets, list):
            continue
        for market in markets:
            if not isinstance(market, dict):
                continue
            outcomes = market.get("outcomes", [])
            if not isinstance(outcomes, list):
                continue
            for outcome in outcomes:
                if not isinstance(outcome, dict):
                    continue
                price = outcome.get("price")
                if not isinstance(price, (int, float)) or price <= 1.0:
                    continue
                decision: KellyDecision = evaluate_kelly(
                    outcome,
                    bankroll=bankroll,
                    model_name=model_name,
                    model_version=model_version,
                )
                title = _row_title(row)
                tour = _row_tour(row)
                if decision.should_bet:
                    line = (
                        f"▶ {title} | {tour} | {price:.2f}"
                        f" | EV {decision.ev_pct:.2f}%"
                        f", edge {decision.edge_pct:.2f}%"
                        f" | Bet {decision.recommended_stake:.2f}u"
                    )
                    lines.append(line)
                    record_bet({"fixture": row, "outcome": outcome, "decision": decision._asdict()})
                    picks_found += 1
                else:
                    lines.append(f"▪ NO BET | {title} | {outcome.get('name','?')} {price:.2f} | {decision.reason}")

    if picks_found == 0:
        lines.append("")
        lines.append("Sin picks válidos según el criterio de edge/EV.")
    return lines
