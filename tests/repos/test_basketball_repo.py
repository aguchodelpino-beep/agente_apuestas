import json
import sqlite3
import pytest
from pathlib import Path
from departments.deportes import basketball_repo as repo


def _prepare_db(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE odds_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                internal_event_id TEXT, sport TEXT, bookmaker TEXT,
                market_key TEXT, outcome_key TEXT, outcome_name TEXT,
                price REAL, captured_at TEXT, event_date TEXT, raw_odd_id TEXT
            )
            """
        )
        conn.executemany(
            """
            INSERT INTO odds_history
                (internal_event_id, sport, bookmaker, market_key,
                 outcome_key, outcome_name, price, captured_at, event_date, raw_odd_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("evt_basket_1","basket","pinnacle","h2h","home","Lakers",2.05,"2026-05-09T10:00:00Z","2026-05-09","a1"),
                ("evt_basket_1","basket","pinnacle","h2h","home","Lakers",1.95,"2026-05-09T12:00:00Z","2026-05-09","a2"),
                ("evt_basket_1","basket","pinnacle","h2h","away","Celtics",2.10,"2026-05-09T10:00:00Z","2026-05-09","b1"),
                ("evt_basket_1","basket","pinnacle","h2h","away","Celtics",2.20,"2026-05-09T12:00:00Z","2026-05-09","b2"),
            ],
        )


def test_load_basket_events_reads_cache(tmp_path: Path, monkeypatch):
    cache_dir = tmp_path / "cache_enriched"
    cache_dir.mkdir()
    (cache_dir / "cachebasket.json").write_text(
        json.dumps({
            "sport": "basket",
            "updated_at": "2026-05-09T08:00:00Z",
            "window_days": 3,
            "items": [{"internal_event_id": "evt_basket_1", "home_team": "Lakers"}],
        }),
        encoding="utf-8",
    )
    monkeypatch.setattr(repo, "CACHE_DIR", cache_dir)
    events = repo.load_basket_events()
    assert len(events) == 1
    assert events[0]["internal_event_id"] == "evt_basket_1"


def test_get_pick_clv_context(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "odds_history.sqlite"
    _prepare_db(db_path)
    monkeypatch.setattr(repo, "HISTORY_DB", db_path)
    clv = repo.get_pick_clv_context(
        "evt_basket_1",
        bookmaker="pinnacle",
        market_key="h2h",
        outcome_key="home",
    )
    assert clv.opening_odds == 2.05
    assert clv.closing_odds == 1.95
    assert clv.clv_pct == pytest.approx(-4.878, abs=1e-2)


def test_get_pick_enriched_clv(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "odds_history.sqlite"
    _prepare_db(db_path)
    monkeypatch.setattr(repo, "HISTORY_DB", db_path)
    enriched = repo.get_pick_enriched(
        "evt_basket_1",
        bookmaker="pinnacle",
        market_key="h2h",
        outcome_key="home",
    )
    clv = enriched["clv"]
    assert isinstance(clv, repo.PickContext)
    assert clv.opening_odds == 2.05
    assert clv.closing_odds == 1.95
    assert clv.clv_pct == pytest.approx(-4.878, abs=1e-2)
