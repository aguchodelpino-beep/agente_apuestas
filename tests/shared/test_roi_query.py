from __future__ import annotations
import sqlite3
import tempfile
import os
import pytest
from shared.roi_query import roi_by, roi_summary, ROIRow


@pytest.fixture
def tmp_db(tmp_path):
    db = str(tmp_path / "test_bets.sqlite")
    conn = sqlite3.connect(db)
    conn.execute("""
        CREATE TABLE bets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            internal_event_id TEXT, sport TEXT, league TEXT,
            market_key TEXT, selection_name TEXT,
            odds_taken REAL, pred_prob REAL, ev_pct REAL,
            full_kelly_pct REAL, fractional_kelly_pct REAL,
            capped_stake_pct REAL, stake REAL, units REAL,
            model_name TEXT, model_version TEXT, ticket_source TEXT,
            event_start_time TEXT, bet_placed_at TEXT,
            result TEXT DEFAULT 'pending', pnl REAL,
            closing_odds REAL, clv_pct REAL
        )
    """)
    conn.executemany(
        "INSERT INTO bets (internal_event_id, sport, league, market_key, selection_name, "
        "odds_taken, pred_prob, ev_pct, stake, model_name, result, pnl, clv_pct) VALUES "
        "(?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [
            ("e1", "tenis", "ATP Roma",      "h2h", "Player A", 2.10, 0.55, 15.5, 100.0, "elo_v1", "win",     110.0, 5.2),
            ("e2", "tenis", "ATP Roma",      "h2h", "Player B", 1.90, 0.48, -8.0,  80.0, "elo_v1", "loss",    -80.0, -3.1),
            ("e3", "futbol","Premier League","h2h", "Home",     2.00, 0.52,  4.0,  50.0, "poisson_v1","win",   50.0, 2.0),
            ("e4", "basket","NBA",           "spread","Lakers", 1.95, 0.53,  3.5,  60.0, "ratings_v1","pending", None, None),
        ],
    )
    conn.commit()
    conn.close()
    return db


def test_roi_by_sport(tmp_db):
    rows = roi_by("sport", db_path=tmp_db)
    sports = {r.value for r in rows}
    assert {"tenis", "futbol", "basket"} == sports


def test_roi_by_league(tmp_db):
    rows = roi_by("league", db_path=tmp_db)
    assert len(rows) == 3


def test_roi_tenis_correct_pnl(tmp_db):
    rows = roi_by("sport", db_path=tmp_db)
    tenis = next(r for r in rows if r.value == "tenis")
    assert tenis.bets == 2
    assert tenis.won == 1
    assert tenis.lost == 1
    assert tenis.pnl == 30.0


def test_roi_summary_totals(tmp_db):
    s = roi_summary(db_path=tmp_db)
    assert s["total_bets"] == 4
    assert s["won"] == 2
    assert s["pending"] == 1
    assert s["total_staked"] == 290.0


def test_invalid_dimension_raises(tmp_db):
    with pytest.raises(ValueError):
        roi_by("ciudad", db_path=tmp_db)
