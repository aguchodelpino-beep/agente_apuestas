from __future__ import annotations

from shared.backtesting import run_backtest
from shared.bets_history_repo import BETS_DB


def handle_estadisticas(db_path: str = BETS_DB) -> str:
    try:
        report = run_backtest(db_path)
    except Exception as e:
        return f"Error generando estadisticas: {e}"

    o = report.overall
    settled = o.get("settled_bets") or 0
    if settled == 0:
        return "Sin apuestas liquidadas todavia."

    won    = o.get("won") or 0
    lost   = o.get("lost") or 0
    pnl    = o.get("total_profit") or 0.0
    staked = o.get("total_stake") or 0.0
    roi    = o.get("roi_pct") or 0.0
    pending = o.get("pending") or 0
    total  = report.total_bets or 0
    wr_str = f"{won/settled*100:.1f}%" if settled else "N/D"

    lines = [
        "ESTADISTICAS GLOBALES",
        "=" * 24,
        f"Total bets : {total}  ({pending} pendientes)",
        f"Ganadas    : {won}",
        f"Perdidas   : {lost}",
        f"Win rate   : {wr_str}",
        f"PnL        : {pnl:+.2f}u",
        f"ROI        : {roi:+.2f}%",
        "",
        "POR DEPORTE",
        "-" * 24,
    ]

    for row in report.by_sport:
        s_won    = row.get("won") or 0
        s_lost   = row.get("lost") or 0
        s_settled= row.get("settled_bets") or 0
        s_pnl    = row.get("total_profit") or 0.0
        s_staked = row.get("total_stake") or 0.0
        s_roi    = row.get("roi_pct") or 0.0
        s_wr     = f"{s_won/s_settled*100:.0f}%" if s_settled else "N/D"
        sport    = (row.get("group_value") or "?").upper()
        lines.append(
            f"{sport} - {s_won}W/{s_lost}L | PnL: {s_pnl:+.2f} | ROI: {s_roi:+.1f}% | WR: {s_wr}"
        )

    lines += ["", "POR LIGA (top 5)", "-" * 24]
    for row in report.by_league[:5]:
        l_pnl    = row.get("total_profit") or 0.0
        l_bets   = row.get("settled_bets") or 0
        league   = row.get("group_value") or "?"
        lines.append(f"  {league}: {l_bets} bets | PnL: {l_pnl:+.2f}u")

    return "\n".join(lines)

if __name__ == "__main__":
    print("SCRIPT OK")
