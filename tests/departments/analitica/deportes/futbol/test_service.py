from __future__ import annotations

from departments.analitica.models import KellyDecision


def _mock_sqlite_empty(path, **kw):
    class Cursor:
        def execute(self, *args, **kwargs):
            return None
        def fetchall(self):
            return []
    class Conn:
        def cursor(self):
            return Cursor()
        def close(self):
            return None
    return Conn()


def test_build_futbol_pick_messages_should_bet(monkeypatch):
    from departments.analitica.deportes.futbol import service as futbol_service

    fixtures = [
        {
            "fixture_id": "fb_1",
            "title": "Barcelona vs Madrid",
            "league": "LaLiga",
            "home": "Barcelona",
            "away": "Madrid",
            "live": True,
            "markets": [
                {
                    "key": "h2h",
                    "outcomes": [
                        {"name": "1", "price": 2.20},
                        {"name": "2", "price": 1.70},
                    ],
                }
            ],
        }
    ]

    recorded = []
    monkeypatch.setattr(futbol_service, "list_live_fixtures", lambda: fixtures)
    monkeypatch.setattr(futbol_service, "record_bet", lambda payload: recorded.append(payload))
    monkeypatch.setattr("sqlite3.connect", _mock_sqlite_empty)

    lines = futbol_service.build_futbol_pick_messages()
    assert any("Bet" in line for line in lines if line.startswith("•"))
    assert len(recorded) == 1


def test_build_futbol_pick_messages_no_bet(monkeypatch):
    from departments.analitica.deportes.futbol import service as futbol_service

    fixtures = [
        {
            "fixture_id": "fb_2",
            "title": "Emelec vs Barcelona SC",
            "league": "LigaPro",
            "home": "Emelec",
            "away": "Barcelona SC",
            "live": True,
            "markets": [
                {
                    "key": "h2h",
                    "outcomes": [
                        {"name": "1", "price": 1.80},
                        {"name": "2", "price": 2.00},
                    ],
                }
            ],
        }
    ]

    recorded = []
    monkeypatch.setattr(futbol_service, "list_live_fixtures", lambda: fixtures)
    monkeypatch.setattr(futbol_service, "record_bet", lambda payload: recorded.append(payload))
    monkeypatch.setattr("sqlite3.connect", _mock_sqlite_empty)
    monkeypatch.setattr(
        futbol_service,
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

    lines = futbol_service.build_futbol_pick_messages()
    assert any("NO BET" in line for line in lines if line.startswith("•"))
    assert len(recorded) == 0
