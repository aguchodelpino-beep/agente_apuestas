import sqlite3
import pytest


def _mock_sqlite_empty(path, *a, **k):
    class C:
        def cursor(self): return type("R", (), {"execute": lambda s,*a,**k: s, "fetchall": lambda s: []})()
        def close(self): pass
    return C()


def test_build_basket_pick_messages_should_bet(monkeypatch):
    from departments.analitica.deportes.basket import service as basket_service

    fixtures = [
        {
            "fixture_id": "bk_1",
            "id": "bk_1",
            "home": "Lakers",
            "away": "Celtics",
            "league": "NBA",
            "live": True,
            "markets": [
                {
                    "key": "h2h",
                    "outcomes": [
                        {"name": "Lakers", "price": 2.10},
                        {"name": "Celtics", "price": 1.75},
                    ],
                }
            ],
        }
    ]

    recorded = []
    monkeypatch.setattr(basket_service, "list_live_fixtures", lambda: fixtures)
    monkeypatch.setattr(basket_service, "record_bet", lambda db, **kw: recorded.append(kw) or 1)
    monkeypatch.setattr("sqlite3.connect", _mock_sqlite_empty)
    # Edge boost simulado: model_prob > implied → EV positivo
    monkeypatch.setattr(
        basket_service,
        "_EDGE_BOOST",
        0.12,  # boost alto para forzar EV > 0 en test
    )

    lines = basket_service.build_basket_pick_messages()
    assert any("Bet" in line for line in lines if line.startswith("•"))


def test_build_basket_pick_messages_no_fixtures(monkeypatch):
    from departments.analitica.deportes.basket import service as basket_service

    monkeypatch.setattr(basket_service, "list_live_fixtures", lambda: [])
    lines = basket_service.build_basket_pick_messages()
    assert lines[0] == "🏀 BASKET PICKS"
    assert any("Sin partidos" in l for l in lines)


def test_build_basket_pick_messages_no_bet(monkeypatch):
    from departments.analitica.deportes.basket import service as basket_service

    fixtures = [
        {
            "fixture_id": "bk_2",
            "home": "Heat", "away": "Bulls", "league": "NBA", "live": True,
            "markets": [{"key": "h2h", "outcomes": [
                {"name": "Heat", "price": 1.50},
                {"name": "Bulls", "price": 2.60},
            ]}],
        }
    ]
    monkeypatch.setattr(basket_service, "list_live_fixtures", lambda: fixtures)
    monkeypatch.setattr(basket_service, "record_bet", lambda db, **kw: None)
    monkeypatch.setattr("sqlite3.connect", _mock_sqlite_empty)
    # Sin edge boost → EV negativo → NO BET
    monkeypatch.setattr(basket_service, "_EDGE_BOOST", 0.0)

    lines = basket_service.build_basket_pick_messages()
    assert any("NO BET" in l or "Sin picks" in l for l in lines)
