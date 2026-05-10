import json
import sqlite3
import pytest
from pathlib import Path
from departments.deportes import tenis_repo as repo


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
                ("evt_tenis_1","tenis","pinnacle","h2h","home","Alcaraz",1.65,"2026-05-09T10:00:00Z","2026-05-09","t1"),
                ("evt_tenis_1","tenis","pinnacle","h2h","home","Alcaraz",1.55,"2026-05-09T14:00:00Z","2026-05-09","t2"),
                ("evt_tenis_1","tenis","pinnacle","h2h","away","Djokovic",2.30,"2026-05-09T10:00:00Z","2026-05-09","t3"),
                ("evt_tenis_1","tenis","pinnacle","h2h","away","Djokovic",2.50,"2026-05-09T14:00:00Z","2026-05-09","t4"),
            ],
        )


def test_load_tenis_events_reads_cache(tmp_path: Path, monkeypatch):
    cache_dir = tmp_path / "cache_enriched"
    cache_dir.mkdir()
    (cache_dir / "cachetenis.json").write_text(
        json.dumps({
            "sport": "tenis",
            "updated_at": "2026-05-09T08:00:00Z",
            "window_days": 3,
            "items": [{"internal_event_id": "evt_tenis_1", "home_team": "Alcaraz"}],
        }),
        encoding="utf-8",
    )
    monkeypatch.setattr(repo, "CACHE_DIR", cache_dir)
    events = repo.load_tenis_events()
    assert len(events) == 1
    assert events[0]["internal_event_id"] == "evt_tenis_1"


def test_get_pick_clv_context(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "odds_history.sqlite"
    _prepare_db(db_path)
    monkeypatch.setattr(repo, "HISTORY_DB", db_path)
    clv = repo.get_pick_clv_context(
        "evt_tenis_1",
        bookmaker="pinnacle",
        market_key="h2h",
        outcome_key="home",
    )
    assert clv.opening_odds == 1.65
    assert clv.closing_odds == 1.55
    assert clv.clv_pct == pytest.approx(-6.060, abs=1e-2)


def test_get_pick_enriched_clv(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "odds_history.sqlite"
    _prepare_db(db_path)
    monkeypatch.setattr(repo, "HISTORY_DB", db_path)
    enriched = repo.get_pick_enriched(
        "evt_tenis_1",
        bookmaker="pinnacle",
        market_key="h2h",
        outcome_key="home",
    )
    clv = enriched["clv"]
    assert isinstance(clv, repo.PickContext)
    assert clv.closing_odds == 1.55
    assert clv.clv_pct == pytest.approx(-6.060, abs=1e-2)
