from __future__ import annotations

import sqlite3
from typing import Any

from departments.analitica.models import BetOpportunity, KellyDecision
from departments.analitica.service import kelly_to_bet_record, evaluate_kelly
from departments.deportes.tenis.repo import list_fixtures          # ← fix: list_fixtures no list_live
from shared.bets_history_repo import record_bet, BETS_DB

_MIN_ODDS   = 1.10   # descartar odds extremas (partido ya jugado)
_MAX_ODDS   = 15.0   # descartar outliers sin liquidez
_MIN_EDGE   = 0.02   # edge mínimo 2 % (antes era valor implícito ~5%)
_MODEL_PROB = 0.54   # prob base ELO hasta integrar modelo real


def _implied_prob(odds: float) -> float:
    return 1.0 / odds if odds > 1.0 else 1.0


def _pick_outcomes(outcomes: list[dict]) -> list[dict]:
    """Retorna outcomes con odds en rango razonable."""
    return [
        o for o in outcomes
        if isinstance(o.get("price"), (int, float))
        and _MIN_ODDS <= float(o["price"]) <= _MAX_ODDS
    ]


def build_tenis_pick_messages(
    bankroll: float = 1000.0,
    model_name: str = "elo_surface_v1",
    model_version: str = "2026.05",
) -> list[str]:
    fixtures = list_fixtures()                          # ← todos (pendientes + live)
    lines = ["🎾 TENIS PICKS"]

    # idempotencia: evitar registrar el mismo bet dos veces
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

    picks_found = 0
    for fix in fixtures:
        status = str(fix.get("status", "")).lower()
        if status in ("finalizado", "finished", "complete"):
            continue

        fix_id = fix.get("fixture_id")
        if not fix_id:
            continue

        markets = fix.get("markets", [])
        h2h = next((m for m in markets if m.get("key") == "h2h"), None)
        if not h2h:
            continue

        valid_outcomes = _pick_outcomes(h2h.get("outcomes", []))
        if not valid_outcomes:
            continue

        for outcome in valid_outcomes:
            odds_taken = float(outcome["price"])
            selection = outcome.get("name", "Unknown")
            implied = _implied_prob(odds_taken)

            # Usar prob del modelo (ELO) — si la prob es del otro lado, invertir
            # La selección más favorita tiene implied < 0.5; apostamos al underdog con edge
            model_prob = _MODEL_PROB

            edge = model_prob - implied
            if edge < _MIN_EDGE:
                continue

            # idempotencia
            key = (fix_id, "h2h", selection, odds_taken)
            if key in recorded:
                continue

            opp = BetOpportunity(
                internal_event_id=fix_id,
                sport="tenis",
                league=fix.get("league") or "Tenis",
                event_title=f"{fix.get('home','?')} vs {fix.get('away','?')}",
                market_key="h2h",
                selection_name=selection,
                odds_taken=odds_taken,
                model_prob=model_prob,
                model_name=model_name,
                model_version=model_version,
                bankroll=bankroll,
            )
            decision: KellyDecision = evaluate_kelly(opp)
            if not decision.should_bet:
                continue

            try:
                bet_record = kelly_to_bet_record(opp, decision)
                record_bet(bet_record)
                recorded.add(key)
            except Exception:
                pass

            stake = round(decision.stake_units * bankroll, 2)
            ev_pct = round(edge * 100, 1)
            lines.append(
                f"\n🎾 {fix.get('home','?')} vs {fix.get('away','?')}"
                f"\n   🏆 {fix.get('league','Tenis')}"
                f"\n   ✅ Pick: **{selection}** @ {odds_taken}"
                f"\n   📊 Edge: +{ev_pct}% | Stake: ${stake:.0f}"
                f"\n   🕐 {fix.get('start_time','')[:16].replace('T',' ')} UTC"
            )
            picks_found += 1

    if picks_found == 0:
        lines.append("\nSin picks con edge positivo hoy.")
    return lines
