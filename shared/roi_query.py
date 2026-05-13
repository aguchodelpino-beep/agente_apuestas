from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Optional


DB_PATH = "data/history/bets_history.sqlite"


@dataclass
class ROIRow:
    dimension: str
    value: str
    bets: int
    won: int
    lost: int
    pending: int
    staked: float
    pnl: float
    roi_pct: float
    avg_odds: float
    avg_ev_pct: Optional[float]
    avg_clv_pct: Optional[float]


def _connect(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def roi_by(
    dimension: str,
    db_path: str = DB_PATH,
    exclude_pending: bool = False,
) -> list[ROIRow]:
    allowed = {"sport", "league", "market_key", "model_name"}
    if dimension not in allowed:
        raise ValueError(f"dimension debe ser uno de {allowed}, recibido: {dimension!r}")

    where = "WHERE result != 'pending'" if exclude_pending else ""

    sql = f"""
        SELECT
            '{dimension}'              AS dimension,
            {dimension}                AS value,
            COUNT(*)                   AS bets,
            SUM(result = 'win')        AS won,
            SUM(result = 'loss')       AS lost,
            SUM(result = 'pending')    AS pending,
            ROUND(SUM(stake), 2)       AS staked,
            ROUND(SUM(COALESCE(pnl, 0)), 2) AS pnl,
            ROUND(
                CASE WHEN SUM(stake) > 0
                     THEN SUM(COALESCE(pnl, 0)) / SUM(stake) * 100
                     ELSE 0 END, 2
            )                          AS roi_pct,
            ROUND(AVG(odds_taken), 4)  AS avg_odds,
            ROUND(AVG(ev_pct), 2)      AS avg_ev_pct,
            ROUND(AVG(clv_pct), 2)     AS avg_clv_pct
        FROM bets
        {where}
        GROUP BY {dimension}
        ORDER BY roi_pct DESC
    """
    conn = _connect(db_path)
    rows = conn.execute(sql).fetchall()
    conn.close()
    return [
        ROIRow(
            dimension=r["dimension"],
            value=r["value"] or "unknown",
            bets=r["bets"],
            won=r["won"] or 0,
            lost=r["lost"] or 0,
            pending=r["pending"] or 0,
            staked=r["staked"] or 0.0,
            pnl=r["pnl"] or 0.0,
            roi_pct=r["roi_pct"] or 0.0,
            avg_odds=r["avg_odds"] or 0.0,
            avg_ev_pct=r["avg_ev_pct"],
            avg_clv_pct=r["avg_clv_pct"],
        )
        for r in rows
    ]


def roi_summary(db_path: str = DB_PATH) -> dict:
    conn = _connect(db_path)
    row = conn.execute("""
        SELECT
            COUNT(*)                        AS total_bets,
            SUM(result = 'win')             AS won,
            SUM(result = 'loss')            AS lost,
            SUM(result = 'pending')         AS pending,
            ROUND(SUM(stake), 2)            AS total_staked,
            ROUND(SUM(COALESCE(pnl,0)), 2)  AS total_pnl,
            ROUND(
                CASE WHEN SUM(stake) > 0
                     THEN SUM(COALESCE(pnl,0)) / SUM(stake) * 100
                     ELSE 0 END, 2
            )                               AS roi_pct,
            ROUND(AVG(odds_taken), 4)       AS avg_odds,
            ROUND(AVG(ev_pct), 2)           AS avg_ev_pct,
            ROUND(AVG(clv_pct), 2)          AS avg_clv_pct
        FROM bets
    """).fetchone()
    conn.close()
    return dict(row)

if __name__ == "__main__":
    print("SCRIPT OK")
