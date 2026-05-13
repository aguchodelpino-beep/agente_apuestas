from shared.service_model_enricher import (
    enrich_pick_with_models,
    enrich_picks_with_models,
    normalize_sport_name,
)


def test_normalize_sport_name():
    assert normalize_sport_name("football") == "futbol"
    assert normalize_sport_name("tennis") == "tenis"
    assert normalize_sport_name("nba") == "basket"


def test_enrich_futbol_pick():
    pick = {
        "event": {
            "home_team": "Barcelona",
            "away_team": "Valencia",
            "odds": {"home": 1.8, "draw": 3.6, "away": 4.2},
        }
    }
    out = enrich_pick_with_models(pick, "futbol")
    assert "model_snapshot" in out
    assert "model_probs" in out
    assert out["model_snapshot"]["sport"] == "futbol"


def test_enrich_tenis_pick():
    pick = {
        "event": {
            "home_team": "Djokovic",
            "away_team": "Murray",
            "surface": "hard",
            "odds": {"home": 1.5, "away": 2.6},
        }
    }
    out = enrich_pick_with_models(pick, "tenis")
    assert "model_snapshot" in out
    assert out["model_snapshot"]["sport"] == "tenis"


def test_enrich_handles_missing_event():
    out = enrich_pick_with_models({}, "basket")
    assert "model_snapshot" not in out


def test_enrich_picks_list():
    picks = [
        {"event": {"home_team": "A", "away_team": "B", "odds": {"home": 1.9, "away": 2.0}}},
        {"event": {"home_team": "C", "away_team": "D", "odds": {"home": 2.1, "away": 1.8}}},
    ]
    out = enrich_picks_with_models(picks, "tenis")
    assert len(out) == 2
