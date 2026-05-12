from __future__ import annotations
from typing import Any

from departments.deportes.basketball_repo import load_basket_events as list_live_fixtures
from departments.analitica.service import kelly_to_bet_record, evaluate_kelly
from departments.analitica.models import BetOpportunity
from shared.prob_from_odds import extract_odds_1x2, fair_probs_1x2

BETS_DB = "data/bets.db"
_EDGE_BOOST = 0.01  # 1% de ventaja informacional asumida


def record_bet(db: str, **kwargs: Any) -> None:
    pass


def _row_title(row: dict[str, Any]) -> str:
    home = row.get("home") or row.get("home_team") or "TBD"
    away = row.get("away") or row.get("away_team") or "TBD"
    return f"{home} vs {away}"


def _row_league(row: dict[str, Any]) -> str:
    league = row.get("league")
    if isinstance(league, str) and league.strip():
        return league.strip()
    return "Basket"


def build_basket_pick_messages(bankroll: float = 1000.0) -> list[str]:
    rows = list_live_fixtures()
    if not rows:
        return ["🏀 BASKET PICKS", "", "Sin partidos en vivo ahora."]

    already_bet: set[tuple] = set()
    lines: list[str] = ["🏀 BASKET PICKS", ""]
    picks_found = 0

    for row in rows:
        fix_id = str(row.get("fixture_id") or row.get("id") or "")
        markets = row.get("markets", [])
        if not isinstance(markets, list):
            continue

        # Buscar market h2h / match_winner
        odds_row = next(
            (m for m in markets if m.get("key") in ("h2h", "match_winner")), None
        )
        if not odds_row:
            continue

        outcomes = odds_row.get("outcomes", [])
        # Calcular fair probs sobre todos los outcomes del mercado
        prices = [float(o["price"]) for o in outcomes if isinstance(o.get("price"), (int, float)) and float(o["price"]) > 1.0]
        if len(prices) < 2:
            continue
        overround = sum(1.0 / p for p in prices)

        for outcome in outcomes:
            price = outcome.get("price")
            if not isinstance(price, (int, float)) or float(price) <= 1.0:
                continue
            odds_taken = float(price)
            fair_p = (1.0 / odds_taken) / overround
            model_prob = min(fair_p + _EDGE_BOOST, 0.95)
            market_key = odds_row.get("key") or "match_winner"
            selection_name = outcome.get("name") or "?"
            key = (fix_id, market_key, selection_name, odds_taken)
            if key in already_bet:
                continue
            already_bet.add(key)

            league = _row_league(row)
            title = _row_title(row)
            opp = BetOpportunity(
                internal_event_id=fix_id,
                sport="basket",
                league=league,
                market_key=market_key,
                selection_name=selection_name,
                odds_taken=odds_taken,
                model_prob=model_prob,
                bankroll=bankroll,
            )
            decision = evaluate_kelly(opp)

            if decision.should_bet:
                bet_record = kelly_to_bet_record(opp, decision, ticket_source="basket_service")
                record_bet(BETS_DB, **{k: v for k, v in bet_record.items() if k not in ("should_bet", "reason")})
                picks_found += 1
                lines.append(
                    f"• {title} [{league}] @ {odds_taken} "
                    f"(EV {decision.ev_pct:.2f}%, edge {decision.edge_pct:.2f}%) "
                    f"→ Bet {decision.recommended_stake:.2f}u"
                )
            else:
                lines.append(
                    f"• {title} [{league}] @ {odds_taken} "
                    f"(EV {decision.ev_pct:.2f}% × NO BET - {decision.reason})"
                )

    if picks_found == 0:
        lines.append("")
        lines.append("Sin picks válidos según el criterio de edge/EV.")
    return lines
