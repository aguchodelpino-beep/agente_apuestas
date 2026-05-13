import pytest

from shared.ensemble_engine import ModelOutput, get_sport_weights, weighted_ensemble


def test_single_model_passthrough():
    out = ModelOutput("poisson", prob_home=0.5, prob_draw=0.25, prob_away=0.25)
    r = weighted_ensemble([out])
    assert abs(r.prob_home - 0.5) < 1e-4
    assert r.models_used == ["poisson"]


def test_two_models_average():
    m1 = ModelOutput("poisson", 0.6, 0.2, 0.2, confidence=1.0)
    m2 = ModelOutput("monte_carlo", 0.4, 0.3, 0.3, confidence=1.0)
    r = weighted_ensemble([m1, m2])
    assert abs(r.prob_home + r.prob_draw + r.prob_away - 1.0) < 1e-6
    assert abs(r.prob_home - 0.5) < 1e-4


def test_custom_weights():
    m1 = ModelOutput("poisson", 0.7, 0.15, 0.15)
    m2 = ModelOutput("edge", 0.4, 0.3, 0.3)
    r = weighted_ensemble([m1, m2], custom_weights={"poisson": 0.8, "edge": 0.2})
    assert r.prob_home > 0.6


def test_probs_always_sum_to_one():
    outputs = [
        ModelOutput("a", 0.3, 0.4, 0.3, confidence=0.5),
        ModelOutput("b", 0.55, 0.2, 0.25, confidence=1.5),
    ]
    r = weighted_ensemble(outputs)
    assert abs(r.prob_home + r.prob_draw + r.prob_away - 1.0) < 1e-6


def test_empty_raises():
    with pytest.raises(ValueError):
        weighted_ensemble([])


def test_sport_weights_keys():
    w = get_sport_weights("futbol")
    assert "poisson" in w
    assert sum(w.values()) == pytest.approx(1.0)
