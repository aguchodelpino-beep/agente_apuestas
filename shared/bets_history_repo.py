from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE_PATH = Path(__file__).resolve().parent.parent
BETS_DB = BASE_PATH / "data" / "history" / "bets_history.sqlite"

_ALLOWED_RESULTS = {"pending", "win", "loss", "push", "void", "half_win", "half_loss"}
_ALLOWED_GROUPS = {"sport", "league", "market_key", "odds_bucket", "model_name", "result"}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _connect(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _odds_bucket(odds_taken: float | None) -> str:
    if odds_taken is None:
        return "unknown"
    if odds_taken < 1.5:
        return "1.00-1.49"
    if odds_taken < 2.0:
        return "1.50-1.99"
    if odds_taken < 3.0:
        return "2.00-2.99"
    return "3.00+"


def _group_expr(group_by: str) -> str:
    if group_by not in _ALLOWED_GROUPS:
        raise ValueError(f"group_by no soportado: {group_by}")

    if group_by == "odds_bucket":
        return (
            "CASE "
            "WHEN odds_taken < 1.5 THEN '1.00-1.49' "
            "WHEN odds_taken < 2.0 THEN '1.50-1.99' "
            "WHEN odds_taken < 3.0 THEN '2.00-2.99' "
            "ELSE '3.00+' END"
        )

    return group_by


def ensure_schema(db_path: str | Path = BETS_DB) -> None:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS bets_history (
                bet_id TEXT PRIMARY KEY,
                placed_at TEXT NOT NULL,
                event_start_time TEXT,
                settled_at TEXT,
                internal_event_id TEXT NOT NULL,
                sport TEXT NOT NULL,
                league TEXT,
                market_key TEXT NOT NULL,
                selection_name TEXT NOT NULL,
                bookmaker_key TEXT,
                odds_taken REAL NOT NULL,
                closing_odds REAL,
                stake REAL NOT NULL,
                result TEXT NOT NULL DEFAULT 'pending',
                profit REAL,
                pred_prob REAL,
                edge_pct REAL,
                model_name TEXT,
                model_version TEXT,
                ticket_source TEXT,
                notes TEXT
            )
            """
        )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_bets_placed_at
            ON bets_history(placed_at)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_bets_sport
            ON bets_history(sport)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_bets_league
            ON bets_history(league)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_bets_market
            ON bets_history(market_key)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_bets_event
            ON bets_history(internal_event_id)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_bets_result
            ON bets_history(result)
            """
        )
        conn.commit()
    finally:
        conn.close()


def compute_profit(result: str, stake: float, odds_taken: float) -> float:
    if result not in _ALLOWED_RESULTS:
        raise ValueError(f"resultado no soportado: {result}")

    if result == "win":
        return round(stake * (odds_taken - 1.0), 2)
    if result == "loss":
        return round(-stake, 2)
    if result in {"push", "void", "pending"}:
        return 0.0
    if result == "half_win":
        return round(stake * (odds_taken - 1.0) / 2.0, 2)
    if result == "half_loss":
        return round(-stake / 2.0, 2)
    return 0.0


def record_bet(db_path: str | Path = BETS_DB, **row: Any) -> str:
    ensure_schema(db_path)

    bet_id = row.get("bet_id") or str(uuid.uuid4())
    placed_at = row.get("placed_at") or utc_now_iso()
    result = row.get("result") or "pending"

    if result not in _ALLOWED_RESULTS:
        raise ValueError(f"resultado no soportado: {result}")

    conn = _connect(db_path)
    try:
        conn.execute(
            """
            INSERT INTO bets_history (
                bet_id,
                placed_at,
                event_start_time,
                settled_at,
                internal_event_id,
                sport,
                league,
                market_key,
                selection_name,
                bookmaker_key,
                odds_taken,
                closing_odds,
                stake,
                result,
                profit,
                pred_prob,
                edge_pct,
                model_name,
                model_version,
                ticket_source,
                notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                bet_id,
                placed_at,
                row.get("event_start_time"),
                row.get("settled_at"),
                row["internal_event_id"],
                row["sport"],
                row.get("league"),
                row["market_key"],
                row["selection_name"],
                row.get("bookmaker_key"),
                float(row["odds_taken"]),
                row.get("closing_odds"),
                float(row["stake"]),
                result,
                row.get("profit"),
                row.get("pred_prob"),
                row.get("edge_pct"),
                row.get("model_name"),
                row.get("model_version"),
                row.get("ticket_source"),
                row.get("notes"),
            ),
        )
        conn.commit()
        return bet_id
    finally:
        conn.close()


def load_bet(db_path: str | Path = BETS_DB, bet_id: str = "") -> dict[str, Any] | None:
    ensure_schema(db_path)
    conn = _connect(db_path)
    try:
        row = conn.execute(
            """
            SELECT *
            FROM bets_history
            WHERE bet_id = ?
            """,
            (bet_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def settle_bet(
    db_path: str | Path = BETS_DB,
    *,
    bet_id: str,
    result: str,
    closing_odds: float | None = None,
    profit: float | None = None,
    settled_at: str | None = None,
) -> dict[str, Any]:
    ensure_schema(db_path)

    if result not in _ALLOWED_RESULTS:
        raise ValueError(f"resultado no soportado: {result}")

    current = load_bet(db_path, bet_id)
    if not current:
        raise KeyError(f"bet_id no existe: {bet_id}")

    stake = float(current["stake"])
    odds_taken = float(current["odds_taken"])
    final_profit = compute_profit(result, stake, odds_taken) if profit is None else round(float(profit), 2)
    final_settled_at = settled_at or utc_now_iso()
    final_closing_odds = closing_odds if closing_odds is not None else current.get("closing_odds")

    conn = _connect(db_path)
    try:
        conn.execute(
            """
            UPDATE bets_history
            SET result = ?,
                closing_odds = ?,
                profit = ?,
                settled_at = ?
            WHERE bet_id = ?
            """,
            (result, final_closing_odds, final_profit, final_settled_at, bet_id),
        )
        conn.commit()
    finally:
        conn.close()

    updated = load_bet(db_path, bet_id)
    if updated is None:
        raise KeyError(f"bet_id no existe tras update: {bet_id}")
    return updated


def summarize_overall(db_path: str | Path = BETS_DB) -> dict[str, Any]:
    ensure_schema(db_path)
    conn = _connect(db_path)
    try:
        row = conn.execute(
            """
            SELECT
                COUNT(*) AS bets,
                SUM(CASE WHEN result != 'pending' THEN 1 ELSE 0 END) AS settled_bets,
                ROUND(COALESCE(SUM(stake), 0), 2) AS total_stake,
                ROUND(COALESCE(SUM(COALESCE(profit, 0)), 0), 2) AS total_profit,
                ROUND(
                    CASE WHEN COALESCE(SUM(stake), 0) > 0
                    THEN (SUM(COALESCE(profit, 0)) * 100.0 / SUM(stake))
                    ELSE 0 END, 2
                ) AS roi_pct,
                ROUND(
                    AVG(
                        CASE
                            WHEN closing_odds IS NOT NULL AND closing_odds > 0
                            THEN ((odds_taken / closing_odds) - 1.0) * 100.0
                        END
                    ),
                    2
                ) AS avg_clv_pct,
                ROUND(
                    AVG(
                        CASE
                            WHEN closing_odds IS NOT NULL AND closing_odds > 0
                            THEN CASE WHEN odds_taken > closing_odds THEN 1.0 ELSE 0.0 END
                        END
                    ) * 100.0,
                    2
                ) AS beat_closing_rate_pct
            FROM bets_history
            """
        ).fetchone()
        return dict(row) if row else {
            "bets": 0,
            "settled_bets": 0,
            "total_stake": 0.0,
            "total_profit": 0.0,
            "roi_pct": 0.0,
            "avg_clv_pct": None,
            "beat_closing_rate_pct": None,
        }
    finally:
        conn.close()


def summarize_by(db_path: str | Path = BETS_DB, group_by: str = "sport") -> list[dict[str, Any]]:
    ensure_schema(db_path)
    group_expr = _group_expr(group_by)

    conn = _connect(db_path)
    try:
        rows = conn.execute(
            f"""
            SELECT
                {group_expr} AS group_value,
                COUNT(*) AS bets,
                SUM(CASE WHEN result != 'pending' THEN 1 ELSE 0 END) AS settled_bets,
                ROUND(COALESCE(SUM(stake), 0), 2) AS total_stake,
                ROUND(COALESCE(SUM(COALESCE(profit, 0)), 0), 2) AS total_profit,
                ROUND(
                    CASE WHEN COALESCE(SUM(stake), 0) > 0
                    THEN (SUM(COALESCE(profit, 0)) * 100.0 / SUM(stake))
                    ELSE 0 END, 2
                ) AS roi_pct,
                ROUND(
                    AVG(
                        CASE
                            WHEN closing_odds IS NOT NULL AND closing_odds > 0
                            THEN ((odds_taken / closing_odds) - 1.0) * 100.0
                        END
                    ),
                    2
                ) AS avg_clv_pct,
                ROUND(
                    AVG(
                        CASE
                            WHEN closing_odds IS NOT NULL AND closing_odds > 0
                            THEN CASE WHEN odds_taken > closing_odds THEN 1.0 ELSE 0.0 END
                        END
                    ) * 100.0,
                    2
                ) AS beat_closing_rate_pct
            FROM bets_history
            GROUP BY {group_expr}
            ORDER BY total_profit DESC, total_stake DESC, group_value ASC
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def list_bets(
    db_path: str | Path = BETS_DB,
    *,
    limit: int = 100,
    sport: str | None = None,
    result: str | None = None,
) -> list[dict[str, Any]]:
    ensure_schema(db_path)

    filters = []
    params: list[Any] = []

    if sport:
        filters.append("sport = ?")
        params.append(sport)
    if result:
        filters.append("result = ?")
        params.append(result)

    where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""
    params.append(limit)

    conn = _connect(db_path)
    try:
        rows = conn.execute(
            f"""
            SELECT *
            FROM bets_history
            {where_sql}
            ORDER BY placed_at DESC, bet_id DESC
            LIMIT ?
            """,
            params,
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
