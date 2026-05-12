from __future__ import annotations

import sqlite3
from typing import Any

from departments.analitica.models import BetOpportunity
from departments.analitica.service import kelly_to_bet_record, evaluate_kelly
from shared.prob_from_odds import extract_odds_1x2, fair_probs_1x2
from departments.deportes.futbol.repo import list_live_fixtures
from shared.bets_history_repo import BETS_DB, record_bet


def build_futbol_pick_messages(
    bankroll: float = 1000.0,
    model_name: str = "poisson_match_v1",
    model_version: str = "2026.05",
) -> list[str]:
    fixtures = list_live_fixtures()
    lines = ["⚽ FUTBOL PICKS"]

    recorded: set[tuple[Any, ...]] = set()
    try:
        conn = sqlite3.connect(BETS_DB)
        cur = conn.cursor()
        cur.execute(
            "SELECT internal_event_id, market_key, selection_name, odds_taken FROM bets"
        )
        for row in cur.fetchall():
            recorded.add((row[0], row[1], row[2], float(row[3])))
        conn.close()
    except Exception:
        pass

    for fix in fixtures:
        if not fix.get("live", True):
            continue

        fix_id = fix.get("fixture_id") or fix.get("id")
        if not fix_id:
            continue

        markets = fix.get("markets", [])
        odds_row = None
        for mk in markets:
            if mk.get("key") in ("h2h", "match_winner"):
                odds_row = mk
                break

        if not odds_row:
            continue

        home_outcome = None
        for out in odds_row.get("outcomes", []):
            if out.get("name") in ("1", "Home", "home"):
                home_outcome = out
                break

        if not home_outcome:
            continue

        odds_taken = float(home_outcome.get("price") or 1.0)
        if not (odds_taken > 1.0):
            continue

        market_key = odds_row.get("key") or "match_winner"
        selection_name = "Home"
        key = (fix_id, market_key, selection_name, odds_taken)
        if key in recorded:
            continue

        # Extraer probabilidades fair desde odds 1X2
        odds_struct = extract_odds_1x2(fix)
        if odds_struct:
            h_odds, d_odds, a_odds = odds_struct
            probs = fair_probs_1x2(h_odds, d_odds, a_odds)
            model_prob = probs["home"]
        else:
            model_prob = 1.0 / odds_taken  # fallback: implied prob sin margen

        league = fix.get("league") or fix.get("competition") or "Futbol"
        opp = BetOpportunity(
            internal_event_id=fix_id,
            sport="futbol",
            league=league,
            market_key=market_key,
            selection_name=selection_name,
            odds_taken=odds_taken,
            model_prob=model_prob,
            bankroll=bankroll,
            model_name=model_name,
            model_version=model_version,
            event_start_time=fix.get("start_time") or fix.get("commence_time"),
        )

        decision = evaluate_kelly(opp)

        if decision.should_bet:
            bet_record = kelly_to_bet_record(opp, decision, ticket_source="futbol_service")
            record_bet(BETS_DB, **{k: v for k, v in bet_record.items() if k not in ('should_bet','reason')})
            recorded.add(key)

        home = fix.get("home") or fix.get("home_team") or "Local"
        away = fix.get("away") or fix.get("away_team") or "Visitante"
        title = fix.get("title") or f"{home} vs {away}"

        if decision.should_bet:
            lines.append(
                f"• {title} [{league}] @ {odds_taken} "
                f"(EV {decision.ev_pct:.2f}%, edge {decision.edge_pct:.2f}%) "
                f"Bet {decision.capped_stake_pct:.2f}% → {decision.recommended_stake:.2f}"
            )
        else:
            lines.append(
                f"• {title} [{league}] @ {odds_taken} "
                f"(EV {decision.ev_pct:.2f}% × NO BET - {decision.reason})"
            )

    if len(lines) == 1:
        lines.append("Sin picks válidos según el criterio de edge/EV.")

    return lines
