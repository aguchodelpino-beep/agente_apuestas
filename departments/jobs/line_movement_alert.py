from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)

BASE_PATH = Path(__file__).parent.parent
HISTORY_DB = BASE_PATH / "data" / "history" / "odds_history.sqlite"

DEFAULT_THRESHOLD_PCT = 5.0
DEFAULT_WINDOW_HOURS = 1


def _prob_decimal(price: float) -> float:
    if price <= 0:
        return 0.0
    return 1.0 / price


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def scan_line_movements(
    *,
    db_path: Path = HISTORY_DB,
    threshold_pct: float = DEFAULT_THRESHOLD_PCT,
    window_hours: float = DEFAULT_WINDOW_HOURS,
) -> List[Dict[str, Any]]:
    if not db_path.exists():
        return []

    conn = _connect(db_path)
    try:
        rows = conn.execute(
            """
            SELECT
                internal_event_id,
                sport,
                market_key,
                outcome_key,
                outcome_name,
                price,
                captured_at
            FROM odds_history
            WHERE bookmaker = 'pinnacle'
              AND captured_at >= datetime('now', ?)
            ORDER BY internal_event_id, sport, market_key, outcome_key, captured_at
            """,
            (f"-{window_hours} hours",),
        ).fetchall()
    finally:
        conn.close()

    grouped: Dict[Tuple[str, str, str, str], List[sqlite3.Row]] = {}
    for row in rows:
        key = (
            row["internal_event_id"],
            row["sport"],
            row["market_key"],
            row["outcome_key"],
        )
        grouped.setdefault(key, []).append(row)

    alerts: List[Dict[str, Any]] = []

    for (_, sport, market_key, outcome_key), snaps in grouped.items():
        if len(snaps) < 2:
            continue

        opening_row = snaps[0]
        closing_row = snaps[-1]

        opening = float(opening_row["price"])
        closing = float(closing_row["price"])

        if opening <= 0 or closing <= 0 or opening == closing:
            continue

        p_open = _prob_decimal(opening)
        p_close = _prob_decimal(closing)
        if p_open == 0:
            continue

        move_pct = abs((p_close - p_open) / p_open) * 100
        if move_pct < threshold_pct:
            continue

        direction = "▽" if closing < opening else "△"

        alerts.append(
            {
                "internal_event_id": opening_row["internal_event_id"],
                "sport": sport,
                "market_key": market_key,
                "outcome_key": outcome_key,
                "outcome_name": opening_row["outcome_name"] or outcome_key,
                "opening_odds": round(opening, 2),
                "closing_odds": round(closing, 2),
                "move_pct": round(move_pct, 2),
                "direction": direction,
                "snap_count": len(snaps),
            }
        )

    alerts.sort(key=lambda x: x["move_pct"], reverse=True)
    return alerts


def format_line_movement_message(alerts: List[Dict[str, Any]]) -> str:
    if not alerts:
        return ""

    lines = ["📉 MOVIMIENTO DE LÍNEA PINNACLE", "━━━━━━━━━━━━━━━━━━━━━━", ""]

    for a in alerts[:10]:
        sport_emoji = {"futbol": "⚽", "tenis": "🎾", "basket": "🏀"}.get(a["sport"], "🏅")
        lines.append(f"{sport_emoji} {a['outcome_name']} | {a['market_key']}")
        lines.append(
            f"   {a['direction']} {a['opening_odds']:.2f} → {a['closing_odds']:.2f}"
            f"  ({a['move_pct']:+.1f}% prob)"
        )
        lines.append("")

    return "\n".join(lines).strip()


def run_line_movement_alert(
    *,
    db_path: Path = HISTORY_DB,
    threshold_pct: float = DEFAULT_THRESHOLD_PCT,
    window_hours: float = DEFAULT_WINDOW_HOURS,
    send_fn=None,
) -> int:
    alerts = scan_line_movements(
        db_path=db_path,
        threshold_pct=threshold_pct,
        window_hours=window_hours,
    )

    if not alerts:
        logger.info("line_movement_alert: sin movimientos >= %.1f%%", threshold_pct)
        return 0

    msg = format_line_movement_message(alerts)

    if send_fn and callable(send_fn):
        send_fn(msg)
    else:
        logger.info("line_movement_alert: %d alertas\n%s", len(alerts), msg)

    return len(alerts)
