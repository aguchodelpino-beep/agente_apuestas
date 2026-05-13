from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional


def _connect(db_path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    _apply_schema(conn)
    conn.commit()
    return conn


def _apply_schema(conn: sqlite3.Connection) -> None:
    schema_path = Path(__file__).parent / "bets_history_schema.sql"
    with open(schema_path) as f:
        conn.executescript(f.read())


def ensure_schema(db_path) -> None:
    _connect(db_path).close()


def record_bet(
    db_path,
    internal_event_id: str,
    sport: str,
    league: str,
    market_key: str,
    selection_name: str,
    bookmaker_key: str,
    odds_taken: float,
    stake: float,
    model_name: str,
    pred_prob: float = 0.0,
    ev_pct: float = 0.0,
    edge_pct: float = 0.0,
    full_kelly_pct: float = 0.0,
    fractional_kelly_pct: float = 0.0,
    capped_stake_pct: float = 0.0,
    units: float = 0.0,
    model_version: Optional[str] = None,
    ticket_source: str = "auto",
    event_start_time: Optional[str] = None,
) -> int:
    conn = _connect(db_path)
    cur = conn.execute(
        """
        INSERT INTO bets (
            internal_event_id, sport, league, market_key, selection_name,
            odds_taken, pred_prob, ev_pct, full_kelly_pct,
            fractional_kelly_pct, capped_stake_pct, stake, units,
            model_name, model_version, ticket_source, event_start_time
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            internal_event_id, sport, league, market_key, selection_name,
            odds_taken, pred_prob, ev_pct, full_kelly_pct,
            fractional_kelly_pct, capped_stake_pct, stake, units,
            model_name, model_version, ticket_source, event_start_time,
        ),
    )
    conn.commit()
    bet_id = cur.lastrowid
    conn.close()
    return bet_id


def load_bet(db_path, bet_id: int) -> Optional[dict]:
    conn = _connect(db_path)
    row = conn.execute("SELECT * FROM bets WHERE id = ?", (bet_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    d = dict(row)
    d["bet_id"] = d["id"]
    return d


def settle_bet(
    db_path,
    *,
    bet_id: int,
    result: str,
    closing_odds: Optional[float] = None,
    settled_at: Optional[str] = None,
) -> dict:
    conn = _connect(db_path)
    row = conn.execute(
        "SELECT odds_taken, stake FROM bets WHERE id = ?", (bet_id,)
    ).fetchone()
    if row is None:
        conn.close()
        raise ValueError(f"bet_id {bet_id} no encontrado")

    odds_taken = row["odds_taken"]
    stake = row["stake"]
    profit = compute_profit(result, stake, odds_taken)

    clv_pct = None
    if closing_odds and closing_odds > 0:
        clv_pct = round((odds_taken / closing_odds - 1) * 100, 2)

    conn.execute(
        """UPDATE bets
           SET result=?, pnl=?, closing_odds=?, clv_pct=?,
               bet_placed_at=COALESCE(?, bet_placed_at)
           WHERE id=?""",
        (result, profit, closing_odds, clv_pct, settled_at, bet_id),
    )
    conn.commit()
    updated = dict(conn.execute("SELECT * FROM bets WHERE id=?", (bet_id,)).fetchone())
    conn.close()
    updated["profit"] = profit
    updated["settled_at"] = settled_at
    return updated


def compute_profit(result: str, stake: float, odds: float) -> float:
    if result == "win":
        return round(stake * (odds - 1), 2)
    if result == "loss":
        return round(-stake, 2)
    if result == "half_win":
        return round(stake / 2 * (odds - 1), 2)
    if result == "half_loss":
        return round(-stake / 2, 2)
    return 0.0


def list_bets(
    db_path,
    *,
    result: Optional[str] = None,
    sport: Optional[str] = None,
    limit: int = 100,
) -> list[dict]:
    conn = _connect(db_path)
    clauses, params = [], []
    if result:
        clauses.append("result = ?")
        params.append(result)
    if sport:
        clauses.append("sport = ?")
        params.append(sport)
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    rows = conn.execute(
        f"SELECT * FROM bets {where} ORDER BY id LIMIT ?", [*params, limit]
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def summarize_overall(db_path) -> dict:
    conn = _connect(db_path)
    row = conn.execute("""
        SELECT
            COUNT(*)                                    AS bets,
            SUM(result != 'pending')                    AS settled_bets,
            SUM(result = 'win')                         AS won,
            SUM(result = 'loss')                        AS lost,
            SUM(result = 'pending')                     AS pending,
            ROUND(SUM(stake), 2)                        AS total_stake,
            ROUND(SUM(COALESCE(pnl, 0)), 2)             AS total_profit,
            ROUND(
                CASE WHEN SUM(stake) > 0
                     THEN SUM(COALESCE(pnl,0)) / SUM(stake) * 100
                     ELSE 0 END, 2)                     AS roi_pct,
            ROUND(AVG(CASE WHEN closing_odds IS NOT NULL
                           AND result != 'pending'
                           THEN CASE WHEN odds_taken >= closing_odds THEN 1.0 ELSE 0.0 END
                      END) * 100, 2)                    AS beat_closing_rate_pct
        FROM bets
    """).fetchone()
    conn.close()
    return dict(row)


def summarize_by(db_path, dimension: str) -> list[dict]:
    allowed = {"sport", "league", "market_key", "model_name", "odds_bucket"}
    if dimension not in allowed:
        raise ValueError(f"dimension debe ser uno de {allowed}")

    if dimension == "odds_bucket":
        source = """
            SELECT *,
              CASE
                WHEN odds_taken < 1.5  THEN '1.01-1.49'
                WHEN odds_taken < 2.0  THEN '1.50-1.99'
                WHEN odds_taken < 3.0  THEN '2.00-2.99'
                ELSE '3.00+'
              END AS odds_bucket
            FROM bets
        """
        group_col = "odds_bucket"
        from_clause = f"({source})"
    else:
        from_clause = "bets"
        group_col = dimension

    conn = _connect(db_path)
    rows = conn.execute(f"""
        SELECT
            {group_col}                              AS group_value,
            COUNT(*)                                 AS bets,
            SUM(result = 'win')                      AS won,
            ROUND(SUM(stake), 2)                     AS total_stake,
            ROUND(SUM(COALESCE(pnl, 0)), 2)          AS total_profit,
            ROUND(
                CASE WHEN SUM(stake) > 0
                     THEN SUM(COALESCE(pnl,0)) / SUM(stake) * 100
                     ELSE 0 END, 2)                  AS roi_pct
        FROM {from_clause}
        GROUP BY {group_col}
        ORDER BY roi_pct DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

BETS_DB = "data/history/bets_history.sqlite"


if __name__ == "__main__":
    print("SCRIPT OK")
