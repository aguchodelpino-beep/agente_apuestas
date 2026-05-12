from __future__ import annotations

from departments.analitica.models import (
    BetOpportunity,
    KellyConfig,
    KellyDecision,
)


def implied_prob_from_odds(odds: float) -> float:
    return round(1 / odds, 10)


def expected_value_pct(model_prob: float, odds: float) -> float:
    ev = (model_prob * odds) - 1
    return round(ev * 100, 2)


def full_kelly_pct(model_prob: float, odds: float) -> float:
    b = odds - 1
    q = 1 - model_prob
    kelly = (b * model_prob - q) / b
    return round(kelly * 100, 2)


def evaluate_kelly(
    opportunity: BetOpportunity,
    config: KellyConfig | None = None,
) -> KellyDecision:
    if config is None:
        config = KellyConfig()
    ev = expected_value_pct(opportunity.model_prob, opportunity.odds_taken)
    fk_pct = full_kelly_pct(opportunity.model_prob, opportunity.odds_taken)

    if ev < config.min_ev_pct or fk_pct <= 0:
        return KellyDecision(
            should_bet=False,
            full_kelly_pct=fk_pct,
            fractional_kelly_pct=0.0,
            capped_stake_pct=0.0,
            recommended_stake=0.0,
            recommended_units=0.0,
            ev_pct=ev,
            reason="ev_bajo",
        )

    fractional_pct = round(fk_pct * config.fractional_kelly, 2)
    max_pct = config.max_stake_pct * 100

    if fractional_pct > max_pct:
        capped_pct = max_pct
        reason = "bet_cap_aplicado"
    else:
        capped_pct = fractional_pct
        reason = "bet_ok"

    stake = round((capped_pct / 100) * opportunity.bankroll, 2)
    units = round(stake / config.unit_size, 2) if config.unit_size > 0 else 0.0

    return KellyDecision(
        should_bet=True,
        full_kelly_pct=fk_pct,
        fractional_kelly_pct=fractional_pct,
        capped_stake_pct=capped_pct,
        recommended_stake=stake,
        recommended_units=units,
        ev_pct=ev,
        reason=reason,
    )


def kelly_to_bet_record(
    opportunity: BetOpportunity,
    decision: KellyDecision,
    ticket_source: str = "auto",
) -> dict:
    return {
        "internal_event_id": opportunity.internal_event_id,
        "sport": opportunity.sport,
        "league": opportunity.league,
        "market_key": opportunity.market_key,
        "selection_name": opportunity.selection_name,
        "odds_taken": opportunity.odds_taken,
        "pred_prob": opportunity.model_prob,
        "ev_pct": decision.ev_pct,
        "full_kelly_pct": decision.full_kelly_pct,
        "fractional_kelly_pct": decision.fractional_kelly_pct,
        "capped_stake_pct": decision.capped_stake_pct,
        "stake": decision.recommended_stake,
        "units": decision.recommended_units,
        "model_name": opportunity.model_name,
        "model_version": opportunity.model_version,
        "event_start_time": opportunity.event_start_time,
        "should_bet": decision.should_bet,
        "reason": decision.reason,
        "ticket_source": ticket_source,
    }


# ── bets report ────────────────────────────────────────────────────────────────

import sqlite3
from pathlib import Path


def _qry(conn: sqlite3.Connection, dimension_col: str) -> list[dict]:
    rows = conn.execute(f"""
        SELECT
            '{dimension_col}'            AS dimension,
            {dimension_col}              AS group_value,
            COUNT(*)                     AS bets,
            SUM(result='win')            AS won,
            SUM(result='loss')           AS lost,
            ROUND(SUM(stake),2)          AS staked,
            ROUND(SUM(COALESCE(pnl,0)),2) AS pnl,
            ROUND(
              CASE WHEN SUM(stake)>0
                   THEN SUM(COALESCE(pnl,0))/SUM(stake)*100
                   ELSE 0 END, 2)        AS roi_pct,
            ROUND(AVG(odds_taken),4)     AS avg_odds,
            ROUND(AVG(clv_pct),2)        AS avg_clv_pct
        FROM bets
        GROUP BY {dimension_col}
        ORDER BY roi_pct DESC
    """).fetchall()
    return [dict(r) for r in rows]


def build_bets_report(db_path) -> dict:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    with open(
        Path(__file__).parent.parent.parent / "shared" / "bets_history_schema.sql"
    ) as f:
        conn.executescript(f.read())

    overall = dict(conn.execute("""
        SELECT
            COUNT(*)                        AS bets,
            SUM(result='win')               AS won,
            SUM(result='loss')              AS lost,
            SUM(result='pending')           AS pending,
            ROUND(SUM(stake),2)             AS staked,
            ROUND(SUM(COALESCE(pnl,0)),2)   AS pnl,
            ROUND(
              CASE WHEN SUM(stake)>0
                   THEN SUM(COALESCE(pnl,0))/SUM(stake)*100
                   ELSE 0 END, 2)           AS roi_pct,
            ROUND(AVG(odds_taken),4)        AS avg_odds,
            ROUND(AVG(clv_pct),2)           AS avg_clv_pct
        FROM bets
    """).fetchone())

    # odds buckets
    conn.execute("""
        CREATE TEMP TABLE IF NOT EXISTS odds_buckets AS
        SELECT *,
          CASE
            WHEN odds_taken < 1.5  THEN '1.01-1.49'
            WHEN odds_taken < 2.0  THEN '1.50-1.99'
            WHEN odds_taken < 2.5  THEN '2.00-2.49'
            WHEN odds_taken < 3.0  THEN '2.50-2.99'
            ELSE '3.00+'
          END AS odds_bucket
        FROM bets
    """)
    by_odds = conn.execute("""
        SELECT
            odds_bucket              AS group_value,
            COUNT(*)                 AS bets,
            SUM(result='win')        AS won,
            ROUND(SUM(stake),2)      AS staked,
            ROUND(SUM(COALESCE(pnl,0)),2) AS pnl,
            ROUND(
              CASE WHEN SUM(stake)>0
                   THEN SUM(COALESCE(pnl,0))/SUM(stake)*100
                   ELSE 0 END, 2)    AS roi_pct
        FROM odds_buckets
        GROUP BY odds_bucket
        ORDER BY odds_bucket
    """).fetchall()

    report = {
        "overall": overall,
        "by_sport": _qry(conn, "sport"),
        "by_league": _qry(conn, "league"),
        "by_market": _qry(conn, "market_key"),
        "by_model": _qry(conn, "model_name"),
        "by_odds_bucket": [dict(r) for r in by_odds],
    }
    conn.close()
    return report
