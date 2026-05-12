from __future__ import annotations

import sqlite3
from unittest.mock import MagicMock, patch

from departments.analitica.models import KellyDecision


def _mock_sqlite_empty(path, **kw):
    conn = MagicMock()
    conn.__enter__ = lambda s: s
    conn.__exit__ = MagicMock(return_value=False)
    cursor = MagicMock()
    cursor.fetchall.return_value = []
    conn.cursor.return_value = cursor
    return conn


def test_build_tenis_pick_messages_idempotent(monkeypatch):
    from departments.analitica.deportes.tenis import service as tenis_service

    fixtures = [
        {
            "fixture_id": "live_t1",
            "title": "Player A vs Player B",
            "league": "ATP Rome",
            "home": "Player A",
            "away": "Player B",
            "live": True,
            "status": "live",
            "start_time": "2026-05-10T15:00:00Z",
            "markets": [
                {
                    "key": "h2h",
                    "outcomes": [
                        {"name": "1", "price": 2.10},
                        {"name": "2", "price": 1.80},
                    ],
                }
            ],
        }
    ]

    recorded_bet_payloads = []

    monkeypatch.setattr(tenis_service, "list_live_fixtures", lambda: fixtures)
    monkeypatch.setattr(
        tenis_service,
        "record_bet",
        lambda db, **kw: recorded_bet_payloads.append(kw) or 1,
    )
    monkeypatch.setattr("sqlite3.connect", _mock_sqlite_empty)

    lines = tenis_service.build_tenis_pick_messages(
        bankroll=1000.0,
        model_name="elo_test",
        model_version="test_v1",
    )

    assert len(lines) >= 2
    assert any("Bet" in line for line in lines if line.startswith("\u2022"))
    assert len(recorded_bet_payloads) == 1


def test_build_tenis_pick_messages_skips_no_bet(monkeypatch):
    from departments.analitica.deportes.tenis import service as tenis_service

    fixtures = [
        {
            "fixture_id": "live_n1",
            "title": "Player C vs Player D",
            "league": "Challengers",
            "home": "Player C",
            "away": "Player D",
            "live": True,
            "status": "live",
            "markets": [
                {
                    "key": "h2h",
                    "outcomes": [
                        {"name": "1", "price": 1.70},
                        {"name": "2", "price": 1.90},
                    ],
                }
            ],
        }
    ]

    recorded_bet_payloads = []

    monkeypatch.setattr(tenis_service, "list_live_fixtures", lambda: fixtures)
    monkeypatch.setattr(
        tenis_service,
        "record_bet",
        lambda db, **kw: recorded_bet_payloads.append(kw) or 1,
    )
    monkeypatch.setattr(
        tenis_service,
        "evaluate_kelly",
        lambda opp: KellyDecision(
            implied_prob=0.60,
            edge_pct=-5.0,
            ev_pct=-3.0,
            full_kelly_pct=0.0,
            fractional_kelly_pct=0.0,
            capped_stake_pct=0.0,
            recommended_stake=0.0,
            recommended_units=0.0,
            should_bet=False,
            reason="edge_negativo",
        ),
    )
    monkeypatch.setattr("sqlite3.connect", _mock_sqlite_empty)

    lines = tenis_service.build_tenis_pick_messages(
        bankroll=1000.0,
        model_name="elo_test",
        model_version="test_v1",
    )

    assert any("NO BET" in line for line in lines if line.startswith("\u2022"))
    assert len(recorded_bet_payloads) == 0
