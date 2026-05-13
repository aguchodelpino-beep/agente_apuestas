"""
Motor de backtesting para picks del agente.
Orquesta settle_pending_bets + genera reporte de rendimiento histórico.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from shared.bets_history_repo import (
    BETS_DB, summarize_overall, summarize_by, list_bets
)


@dataclass
class BacktestReport:
    overall: dict
    by_sport: list[dict]
    by_league: list[dict]
    by_market: list[dict]
    by_odds_bucket: list[dict]
    total_bets: int
    settled_bets: int


def run_backtest(db_path: str = BETS_DB) -> BacktestReport:
    overall      = summarize_overall(db_path)
    by_sport     = summarize_by(db_path, "sport")
    by_league    = summarize_by(db_path, "league")
    by_market    = summarize_by(db_path, "market_key")
    by_odds      = summarize_by(db_path, "odds_bucket")
    return BacktestReport(
        overall=overall,
        by_sport=by_sport,
        by_league=by_league,
        by_market=by_market,
        by_odds_bucket=by_odds,
        total_bets=overall.get("bets", 0),
        settled_bets=overall.get("settled_bets", 0),
    )


def format_backtest_report(report: BacktestReport) -> str:
    o = report.overall
    lines = [
        "📊 REPORTE DE BACKTESTING",
        "",
        f"Total apuestas : {report.total_bets}",
        f"Resueltas      : {report.settled_bets}",
        f"Pendientes     : {o.get('pending', 0)}",
        f"Ganadas        : {o.get('won', 0)}",
        f"Perdidas       : {o.get('lost', 0)}",
        f"Stake total    : {o.get('total_stake', 0):.2f}u",
        f"P&L total      : {o.get('total_profit', 0):+.2f}u",
        f"ROI            : {o.get('roi_pct', 0):+.2f}%",
        f"Beat CLV rate  : {o.get('beat_closing_rate_pct') or 'N/A'}%",
    ]

    if report.by_sport:
        lines += ["", "── Por deporte ──"]
        for r in report.by_sport:
            lines.append(
                f"  {r['group_value']:10} | {r['bets']:3} bets | "
                f"ROI {r['roi_pct']:+.2f}% | P&L {r['total_profit']:+.2f}u"
            )

    if report.by_odds_bucket:
        lines += ["", "── Por rango de odds ──"]
        for r in report.by_odds_bucket:
            lines.append(
                f"  {r['group_value']:12} | {r['bets']:3} bets | "
                f"ROI {r['roi_pct']:+.2f}% | P&L {r['total_profit']:+.2f}u"
            )

    return "\n".join(lines)

if __name__ == "__main__":
    print("SCRIPT OK")
