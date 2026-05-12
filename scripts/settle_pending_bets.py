#!/usr/bin/env python3
"""
Cruza apuestas pending en bets_history.sqlite contra el cache de fixtures.
Si el partido terminó y hay ganador, llama settle_bet() automáticamente.

Uso:
    python scripts/settle_pending_bets.py          # todos los deportes
    python scripts/settle_pending_bets.py tenis
    python scripts/settle_pending_bets.py --dry-run
"""
from __future__ import annotations
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.bets_history_repo import BETS_DB, list_bets, settle_bet

CACHE_DIR = ROOT / "data" / "cache"
SPORTS    = ["tenis", "futbol", "basket"]

FINISHED_STATUSES = {
    "finished", "finalizado", "complete", "completed",
    "closed", "ended", "ft", "aot", "post",
}


def _load_cache(sport: str) -> list[dict]:
    """Carga el cache más reciente del deporte."""
    sport_dir = CACHE_DIR / sport
    if not sport_dir.exists():
        return []
    files = sorted(sport_dir.glob("*.json"), reverse=True)
    if not files:
        return []
    try:
        return json.loads(files[0].read_text(encoding="utf-8"))
    except Exception:
        return []


def _is_finished(fixture: dict) -> bool:
    status = str(fixture.get("status", "")).lower()
    return status in FINISHED_STATUSES


def _resolve_result(bet: dict, fixture: dict) -> str | None:
    """
    Determina win/loss comparando selection_name contra el ganador del fixture.
    Retorna 'win', 'loss', o None si no se puede determinar.
    """
    # Usar get con sentinel para distinguir False de None
    _s = object()
    winner = fixture.get("winner", _s)
    if winner is _s:
        winner = fixture.get("home_winner", None)
    selection = bet["selection_name"].lower().strip()
    home = str(fixture.get("home") or fixture.get("home_team") or "").lower().strip()
    away = str(fixture.get("away") or fixture.get("away_team") or "").lower().strip()

    # h2h directo: winner=True → home ganó, winner=False → away ganó
    if winner is True:
        return "win" if selection in (home, "home") else "loss"
    if winner is False:
        return "win" if selection in (away, "away") else "loss"
    # winner es string con el nombre del ganador
    if isinstance(winner, str) and winner:
        winner_low = winner.lower().strip()
        if selection == winner_low:
            return "win"
        if selection in (home, away):
            return "loss"

    # Fallback: buscar score para h2h tenis/basket
    score = fixture.get("score") or fixture.get("scores")
    if score and isinstance(score, dict):
        home_pts = score.get("home", 0) or 0
        away_pts = score.get("away", 0) or 0
        if home_pts == away_pts:
            return None  # empate / void
        home_won = home_pts > away_pts
        if selection in (home, "home"):
            return "win" if home_won else "loss"
        if selection in (away, "away"):
            return "win" if not home_won else "loss"

    return None


def settle_sport(sport: str, dry_run: bool = False) -> dict:
    fixtures = _load_cache(sport)
    finished = {
        str(f.get("fixture_id") or f.get("id")): f
        for f in fixtures
        if _is_finished(f)
    }

    pending = [b for b in list_bets(BETS_DB, result="pending", sport=sport)]
    settled = skipped = errors = 0

    for bet in pending:
        eid = str(bet["internal_event_id"])
        fix  = finished.get(eid)
        if not fix:
            skipped += 1
            continue

        result = _resolve_result(bet, fix)
        if not result:
            skipped += 1
            continue

        closing_odds = None
        for m in fix.get("markets", []):
            if m.get("key") == bet["market_key"]:
                for o in m.get("outcomes", []):
                    if o.get("name", "").lower() == bet["selection_name"].lower():
                        closing_odds = float(o.get("price", 0)) or None

        now = datetime.now(timezone.utc).isoformat()

        if dry_run:
            print(f"  [DRY] bet_id={bet['id']} {sport} {bet['selection_name']}"
                  f" → {result}  closing={closing_odds}")
            settled += 1
            continue

        try:
            updated = settle_bet(
                BETS_DB,
                bet_id=bet["id"],
                result=result,
                closing_odds=closing_odds,
                settled_at=now,
            )
            print(f"  ✅ bet_id={bet['id']} {sport} {bet['selection_name']}"
                  f" → {result}  PnL={updated['pnl']:+.2f}  CLV={updated.get('clv_pct') or 'n/a'}")
            settled += 1
        except Exception as e:
            print(f"  ❌ bet_id={bet['id']} error: {e}")
            errors += 1

    return {"sport": sport, "settled": settled, "skipped": skipped, "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description="Settle pending bets from cache")
    parser.add_argument("sports", nargs="*", default=SPORTS)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    mode = "DRY-RUN" if args.dry_run else "LIVE"
    print(f"=== settle_pending_bets [{mode}] {datetime.now().strftime('%Y-%m-%d %H:%M')} ===")

    totals = {"settled": 0, "skipped": 0, "errors": 0}
    for sport in args.sports:
        if sport not in SPORTS:
            print(f"⚠️  Deporte desconocido: {sport}")
            continue
        print(f"\n── {sport.upper()} ──")
        r = settle_sport(sport, dry_run=args.dry_run)
        for k in totals:
            totals[k] += r[k]

    print(f"\n=== TOTAL: settled={totals['settled']} skipped={totals['skipped']} errors={totals['errors']} ===")
    return 0 if totals["errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
