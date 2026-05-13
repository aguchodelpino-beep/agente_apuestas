from shared.model_hub import (
    build_basket_snapshot,
    build_futbol_snapshot,
    build_model_snapshot,
    build_tenis_snapshot,
)


def test_build_futbol_snapshot():
    event = {
        "home_team": "Barcelona",
        "away_team": "Valencia",
        "odds": {"home": 1.8, "draw": 3.6, "away": 4.2, "over": 1.9, "under": 1.9},
        "total_line": 2.5,
    }
    result = build_futbol_snapshot(event)
    assert result is not None
    assert result["sport"] == "futbol"
    assert "ensemble" in result
    assert len(result["market_probs"]) >= 3


def test_build_tenis_snapshot():
    event = {
        "home_team": "Djokovic",
        "away_team": "Murray",
        "surface": "hard",
        "odds": {"home": 1.5, "away": 2.6},
    }
    result = build_tenis_snapshot(event)
    assert result is not None
    assert result["sport"] == "tenis"
    assert result["elo"]["prob_a"] > 0
    assert len(result["market_probs"]) >= 2


def test_build_basket_snapshot():
    event = {
        "home_team": "Celtics",
        "away_team": "Heat",
        "stats": {
            "home_ortg": 118.0,
            "home_drtg": 109.0,
            "home_pace": 99.0,
            "away_ortg": 112.0,
            "away_drtg": 113.0,
            "away_pace": 97.0,
        },
        "odds": {"home": 1.65, "away": 2.3, "over": 1.91, "under": 1.91, "spread_home": 1.9, "spread_away": 1.9},
        "spread": 4.5,
        "total_line": 221.5,
    }
    result = build_basket_snapshot(event)
    assert result is not None
    assert result["sport"] == "basket"
    assert result["ratings"]["projected_total"] > 0
    assert len(result["market_probs"]) >= 5


def test_dispatcher_unknown_returns_none():
    assert build_model_snapshot("cricket", {}) is None


def test_dispatcher_routes_futbol():
    event = {"odds": {"home": 2.0, "away": 3.5}}
    result = build_model_snapshot("futbol", event)
    assert result is not None
    assert result["sport"] == "futbol"
