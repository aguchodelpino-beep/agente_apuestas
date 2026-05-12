import sqlite3
import tempfile
import os
import pytest
from shared.backtesting import run_backtest, format_backtest_report, BacktestReport

DDL = open("shared/bets_history_schema.sql").read()

@pytest.fixture
def tmp_db():
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
        path = f.name
    conn = sqlite3.connect(path)
    conn.executescript(DDL)
    # Insertar bets de prueba
    conn.executemany("""
        INSERT INTO bets (internal_event_id, sport, league, market_key,
            selection_name, odds_taken, pred_prob, ev_pct, stake, units,
            model_name, ticket_source, result, pnl)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, [
        ("ev_1","futbol","LaLiga","match_winner","Home",2.10,0.55,15.5,30.0,3.0,"kelly_v1","test","win",33.0),
        ("ev_2","futbol","LaLiga","match_winner","Away",1.80,0.60,8.0, 20.0,2.0,"kelly_v1","test","loss",-20.0),
        ("ev_3","tenis","ATP","h2h","Alcaraz",1.90,0.58,10.2,25.0,2.5,"kelly_v1","test","win",22.5),
        ("ev_4","basket","NBA","h2h","Lakers",2.20,0.52,14.4,15.0,1.5,"kelly_v1","test","pending",None),
    ])
    conn.commit()
    conn.close()
    yield path
    os.unlink(path)


def test_run_backtest_returns_report(tmp_db):
    report = run_backtest(tmp_db)
    assert isinstance(report, BacktestReport)
    assert report.total_bets == 4
    assert report.settled_bets == 3


def test_backtest_overall_roi(tmp_db):
    report = run_backtest(tmp_db)
    o = report.overall
    assert o["won"] == 2
    assert o["lost"] == 1
    assert o["total_profit"] == pytest.approx(35.5, abs=0.1)
    assert o["roi_pct"] > 0


def test_backtest_by_sport(tmp_db):
    report = run_backtest(tmp_db)
    sports = {r["group_value"] for r in report.by_sport}
    assert "futbol" in sports
    assert "tenis" in sports


def test_format_report_contains_key_fields(tmp_db):
    report = run_backtest(tmp_db)
    text = format_backtest_report(report)
    assert "BACKTESTING" in text
    assert "ROI" in text
    assert "P&L" in text
    assert "futbol" in text.lower() or "tenis" in text.lower()
