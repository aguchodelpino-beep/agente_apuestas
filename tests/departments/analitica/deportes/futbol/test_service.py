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
            "id": "fb_1",
            "title": "Barcelona vs Madrid",
            "league": "LaLiga",
            "home": "Barcelona",
            "away": "Madrid",
            "home_team": "Barcelona",
            "away_team": "Madrid",
            "live": True,
            "odds": {
                "Barcelona": 2.20,
                "Draw": 3.40,
                "Madrid": 1.70,
            },
            "markets": [
                {
                    "key": "match_winner",
                    "outcomes": [
                        {"name": "Home", "price": 2.20},
                        {"name": "Away", "price": 1.70},
                    ],
                }
            ],
        }
    ]

    recorded = []
    monkeypatch.setattr(futbol_service, "list_live_fixtures", lambda: fixtures)
    monkeypatch.setattr(futbol_service, "record_bet", lambda db, **kw: recorded.append(kw) or 1)
    monkeypatch.setattr("sqlite3.connect", _mock_sqlite_empty)
    # Simular que el modelo tiene edge: model_prob > implied_prob del mercado
    # odds_home=2.20 → implied=0.454; damos model_prob=0.55 → EV = 0.55*2.20-1 = +21%
    # Parchear en el namespace del service (ya importó las funciones)
    monkeypatch.setattr(futbol_service, "extract_odds_1x2", lambda fix: (2.20, 3.40, 1.70))
    monkeypatch.setattr(futbol_service, "fair_probs_1x2", lambda h, d, a: {
        "home": 0.55, "draw": 0.28, "away": 0.17, "overround": 1.077
    })

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
    monkeypatch.setattr(futbol_service, "record_bet", lambda db, **kw: recorded.append(kw) or 1)
    monkeypatch.setattr("sqlite3.connect", _mock_sqlite_empty)
    # Simular que el modelo tiene edge: model_prob > implied_prob del mercado
    # odds_home=2.20 → implied=0.454; damos model_prob=0.55 → EV = 0.55*2.20-1 = +21%
    # Parchear en el namespace del service (ya importó las funciones)
    monkeypatch.setattr(futbol_service, "extract_odds_1x2", lambda fix: (2.20, 3.40, 1.70))
    monkeypatch.setattr(futbol_service, "fair_probs_1x2", lambda h, d, a: {
        "home": 0.55, "draw": 0.28, "away": 0.17, "overround": 1.077
    })
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
