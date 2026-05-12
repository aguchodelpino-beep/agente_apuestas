from __future__ import annotations
import sqlite3
from departments.analitica.models import BetOpportunity, KellyDecision
from departments.analitica.service import kelly_to_bet_record, evaluate_kelly
from departments.deportes.tenis.repo import list_fixtures, list_live_fixtures

from shared.bets_history_repo import record_bet, BETS_DB

def _get_candidate_fixtures() -> list[dict]:
    try:
        live = list_live_fixtures()
        if live:
            return live
    except Exception:
        pass
    return list_fixtures()


_MIN_ODDS    = 1.10
_MAX_ODDS    = 15.0
_MIN_EDGE    = 0.0    # filtro real es Kelly
_MAX_OVER    = 1.12   # descartar libros con margen > 12%
_EDGE_BOOST  = 0.02   # descuento de margen que aplicamos como ventaja propia


def _valid_outcomes(outcomes: list[dict]) -> list[dict]:
    return [
        o for o in outcomes
        if isinstance(o.get("price"), (int, float))
        and _MIN_ODDS <= float(o["price"]) <= _MAX_ODDS
    ]


def _fair_probs(outcomes: list[dict]) -> dict[str, float]:
    """Calcula probabilidades fair removiendo margen del libro."""
    prices = [float(o["price"]) for o in outcomes]
    overround = sum(1.0 / p for p in prices)
    if overround > _MAX_OVER or overround <= 0:
        return {}
    return {
        o["name"]: round((1.0 / float(o["price"])) / overround, 4)
        for o in outcomes
    }


def build_tenis_pick_messages(
    bankroll: float = 1000.0,
    model_name: str = "elo_surface_v1",
    model_version: str = "2026.05",
) -> list[str]:
    fixtures = _get_candidate_fixtures()
    lines = ["🎾 TENIS PICKS"]

    recorded: set = set()
    try:
        conn = sqlite3.connect(BETS_DB)
        cur = conn.cursor()
        cur.execute("SELECT internal_event_id, market_key, selection_name, odds_taken FROM bets")
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

        h2h = next((m for m in fix.get("markets", []) if m.get("key") == "h2h"), None)
        if not h2h:
            continue

        valid = _valid_outcomes(h2h.get("outcomes", []))
        if len(valid) < 2:
            continue

        probs = _fair_probs(valid)
        if not probs:
            continue

        # Tomar solo el outcome con mayor edge por partido
        best = max(
            valid,
            key=lambda o: (min(probs.get(o["name"], 0.0) + _EDGE_BOOST, 0.95) - 1.0 / float(o["price"]))
        )
        outcomes_to_eval = [best]

        for outcome in outcomes_to_eval:
            odds_taken = float(outcome["price"])
            selection = outcome.get("name", "Unknown")
            fair_p = probs.get(selection, 0.0)

            model_prob = min(fair_p + _EDGE_BOOST, 0.95)
            implied_p  = 1.0 / odds_taken
            edge       = model_prob - implied_p

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

            ev_pct = round(edge * 100, 2)
            home = fix.get('home', '?')
            away = fix.get('away', '?')
            league = fix.get('league', 'Tenis')

            if decision.should_bet:
                try:
                    bet_record = kelly_to_bet_record(opp, decision)
                    record_bet(BETS_DB, **{k: v for k, v in bet_record.items() if k not in ('should_bet','reason')})
                    recorded.add(key)
                except Exception as e:
                    import sys; print(f"[record_bet ERROR] {e}", file=sys.stderr)
                lines.append(
                    f"• {home} vs {away} [{league}] @ {odds_taken} "
                    f"(EV {ev_pct:.2f}%, edge {ev_pct:.2f}%) "
                    f"Bet {decision.capped_stake_pct:.2f}% → {decision.recommended_stake:.2f}"
                )
                picks_found += 1
            else:
                lines.append(
                    f"• {home} vs {away} [{league}] @ {odds_taken} "
                    f"(EV {ev_pct:.2f}% × NO BET - {decision.reason})"
                )

    if picks_found == 0:
        lines.append("\nSin picks con edge positivo hoy.")
    return lines
