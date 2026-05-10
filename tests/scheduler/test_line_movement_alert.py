import sqlite3
import pytest
from pathlib import Path
from jobs.line_movement_alert import (
    scan_line_movements,
    format_line_movement_message,
    run_line_movement_alert,
)


def _make_db(db_path: Path, rows: list) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE odds_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                internal_event_id TEXT, sport TEXT, bookmaker TEXT,
                market_key TEXT, outcome_key TEXT, outcome_name TEXT,
                price REAL, captured_at TEXT, event_date TEXT, raw_odd_id TEXT
            )
        """)
        conn.executemany(
            """INSERT INTO odds_history
               (internal_event_id, sport, bookmaker, market_key,
                outcome_key, outcome_name, price, captured_at, event_date, raw_odd_id)
               VALUES (?,?,?,?,?,?,?,datetime('now', ? || ' minutes'),?,?)""",
            rows,
        )


def test_scan_returns_empty_when_no_db(tmp_path):
    alerts = scan_line_movements(db_path=tmp_path / "nonexistent.sqlite")
    assert alerts == []


def test_scan_detects_significant_movement(tmp_path):
    db = tmp_path / "odds.sqlite"
    _make_db(db, [
        ("evt1","tenis","pinnacle","h2h","home","Alcaraz",2.20,"-50","2026-05-10","r1"),
        ("evt1","tenis","pinnacle","h2h","home","Alcaraz",1.80,"-5", "2026-05-10","r2"),
    ])
    alerts = scan_line_movements(db_path=db, threshold_pct=5.0, window_hours=1)
    assert len(alerts) == 1
    assert alerts[0]["outcome_name"] == "Alcaraz"
    assert alerts[0]["move_pct"] > 5.0
    assert alerts[0]["direction"] == "▽"


def test_scan_ignores_small_movement(tmp_path):
    db = tmp_path / "odds.sqlite"
    _make_db(db, [
        ("evt2","futbol","pinnacle","h2h","home","Real Madrid",2.00,"-50","2026-05-10","r1"),
        ("evt2","futbol","pinnacle","h2h","home","Real Madrid",2.02,"-5", "2026-05-10","r2"),
    ])
    alerts = scan_line_movements(db_path=db, threshold_pct=5.0, window_hours=1)
    assert alerts == []


def test_format_message_empty():
    assert format_line_movement_message([]) == ""


def test_format_message_with_alerts():
    alerts = [{
        "sport": "tenis", "outcome_name": "Alcaraz", "market_key": "h2h",
        "opening_odds": 2.20, "closing_odds": 1.80, "move_pct": 11.5,
        "direction": "▽", "snap_count": 3,
    }]
    msg = format_line_movement_message(alerts)
    assert "Alcaraz" in msg
    assert "2.20" in msg
    assert "1.80" in msg
    assert "▽" in msg


def test_run_calls_send_fn(tmp_path):
    db = tmp_path / "odds.sqlite"
    _make_db(db, [
        ("evt3","basket","pinnacle","h2h","home","Lakers",2.10,"-50","2026-05-10","r1"),
        ("evt3","basket","pinnacle","h2h","home","Lakers",1.75,"-5", "2026-05-10","r2"),
    ])
    sent = []
    count = run_line_movement_alert(
        db_path=db, threshold_pct=5.0, window_hours=1,
        send_fn=lambda msg: sent.append(msg),
    )
    assert count == 1
    assert len(sent) == 1
    assert "Lakers" in sent[0]
