"""Tests para scripts/settle_pending_bets.py"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from shared.bets_history_repo import record_bet, list_bets, ensure_schema
from scripts.settle_pending_bets import settle_sport, _resolve_result, _is_finished


def _make_db(tmp_path) -> str:
    db = str(tmp_path / "bets.sqlite")
    ensure_schema(db)
    return db


def _insert(db, event_id, sport, selection, odds=2.0, stake=100.0):
    return record_bet(
        db,
        internal_event_id=event_id,
        sport=sport,
        league="Test League",
        market_key="h2h",
        selection_name=selection,
        bookmaker_key="test",
        odds_taken=odds,
        stake=stake,
        model_name="test_model",
    )


def test_is_finished_statuses():
    assert _is_finished({"status": "finished"})
    assert _is_finished({"status": "FT"})
    assert not _is_finished({"status": "scheduled"})
    assert not _is_finished({})


def test_resolve_result_home_win():
    bet = {"selection_name": "Djokovic", "market_key": "h2h"}
    fix = {"home": "Djokovic", "away": "Alcaraz", "winner": True}
    assert _resolve_result(bet, fix) == "win"


def test_resolve_result_away_win():
    bet = {"selection_name": "Alcaraz", "market_key": "h2h"}
    fix = {"home": "Djokovic", "away": "Alcaraz", "winner": False}
    assert _resolve_result(bet, fix) == "win"


def test_resolve_result_loss():
    bet = {"selection_name": "Djokovic", "market_key": "h2h"}
    fix = {"home": "Djokovic", "away": "Alcaraz", "winner": False}
    assert _resolve_result(bet, fix) == "loss"


def test_resolve_result_unknown_returns_none():
    bet = {"selection_name": "Unknown", "market_key": "h2h"}
    fix = {"home": "Djokovic", "away": "Alcaraz"}
    assert _resolve_result(bet, fix) is None


def test_settle_sport_settles_finished(tmp_path, monkeypatch):
    db = _make_db(tmp_path)
    bet_id = _insert(db, "evt_001", "tenis", "Djokovic", odds=2.10, stake=100.0)

    fixtures = [{"fixture_id": "evt_001", "status": "finished",
                 "home": "Djokovic", "away": "Alcaraz", "winner": True, "markets": []}]

    import scripts.settle_pending_bets as m
    monkeypatch.setattr(m, "BETS_DB", db)
    monkeypatch.setattr(m, "_load_cache", lambda sport: fixtures)

    result = m.settle_sport("tenis")
    assert result["settled"] == 1
    assert result["errors"] == 0

    bets = list_bets(db, result="win")
    assert len(bets) == 1
    assert bets[0]["pnl"] == 110.0  # stake*(odds-1) = 100*1.10


def test_settle_sport_skips_pending_fixture(tmp_path, monkeypatch):
    db = _make_db(tmp_path)
    _insert(db, "evt_002", "futbol", "Home")

    fixtures = [{"fixture_id": "evt_002", "status": "scheduled",
                 "home": "Home", "away": "Away", "markets": []}]

    import scripts.settle_pending_bets as m
    monkeypatch.setattr(m, "BETS_DB", db)
    monkeypatch.setattr(m, "_load_cache", lambda sport: fixtures)

    result = m.settle_sport("futbol")
    assert result["settled"] == 0
    assert result["skipped"] == 1
