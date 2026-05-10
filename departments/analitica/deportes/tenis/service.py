from __future__ import annotations

import sqlite3

from typing import Any

from departments.analitica.models import BetOpportunity, KellyDecision
from departments.analitica.service import kelly_to_bet_record, evaluate_kelly
from departments.deportes.tenis.repo import list_live_fixtures, get_fixture_by_id
from shared.bets_history_repo import record_bet, BETS_DB


def build_tenis_pick_messages(
    bankroll: float = 1000.0,
    model_name: str = "elo_surface_v1",
    model_version: str = "2026.05",
) -> list[str]:
    fixtures = list_live_fixtures()
    lines = ["🎾 TENIS PICKS"]

    # idempotencia: leer bets ya registrados para este run
    recorded: set = set()
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
        if not fix.get("live") or fix.get("status") == "finalizado":
            continue

        fix_id = fix.get("fixture_id")
        if not fix_id:
            continue

        # 1. Asumir market: match_winner, casa1 como favorito
        #    (esto es solo un ejemplo; tú puedes afinar el mercado)
        markets = fix.get("markets", [])
        odds_row = None
        for mk in markets:
            if mk.get("key") == "h2h":
                odds_row = mk
                break

        if not odds_row:
            continue

        home_outcome = None
        for out in odds_row.get("outcomes", []):
            if out.get("name") == "1" or out.get("name") == "Home":
                home_outcome = out
                break

        if not home_outcome:
            continue

        # 2. mock model_prob (ejemplo 0.55); tú reemplazas con tu ELO/CLV
        model_prob = 0.55

        odds_taken = float(home_outcome.get("price") or 1.0)
        if not (odds_taken > 1.0):
            continue

        # 2b. idempotencia: saltar si ya existe este combo en bets
        key = (fix_id, "match_winner", "Home", odds_taken)
        if key in recorded:
            continue

        # 3. formar BetOpportunity
        opp = BetOpportunity(
            internal_event_id=fix_id,
            sport="tenis",
            league=fix.get("league") or "Tenis",
            market_key="match_winner",
            selection_name="Home",
            odds_taken=odds_taken,
            model_prob=model_prob,
            bankroll=bankroll,
            model_name=model_name,
            model_version=model_version,
            event_start_time=fix.get("start_time") or fix.get("commence_time"),
        )

        # 4. aplicar Kelly
        decision = evaluate_kelly(opp)

        # 5. guardar registro solo si should_bet
        if decision.should_bet:
            bet_record = kelly_to_bet_record(opp, decision, ticket_source="tenis_service")
            record_bet(bet_record)
            recorded.add(key)

        # 6. añadir texto al mensaje
        home = fix.get("home") or fix.get("home_team") or "Local"
        away = fix.get("away") or fix.get("away_team") or "Visitante"
        title = fix.get("title") or f"{home} vs {away}"
        league = fix.get("league") or fix.get("competition") or "Tenis"

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
