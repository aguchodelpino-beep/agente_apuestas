from departments.deportes.futbol.poisson_model import poisson_match_probs, xg_from_event


def test_probabilities_sum_to_one():
    r = poisson_match_probs(1.5, 1.1)
    assert abs(r.home_win + r.draw + r.away_win - 1.0) < 1e-6


def test_btts_complement():
    r = poisson_match_probs(1.5, 1.1)
    assert abs(r.btts_yes + r.btts_no - 1.0) < 1e-6


def test_over_under_complement():
    r = poisson_match_probs(1.5, 1.1)
    assert abs(r.over_2_5 + r.under_2_5 - 1.0) < 1e-6


def test_strong_home_favors_home():
    r = poisson_match_probs(3.0, 0.5)
    assert r.home_win > 0.75


def test_xg_from_event_direct():
    event = {"xg_home": 1.6, "xg_away": 0.9}
    result = xg_from_event(event)
    assert result == (1.6, 0.9)


def test_xg_from_event_odds_fallback():
    event = {"odds": {"home": 1.8, "away": 3.5}}
    result = xg_from_event(event)
    assert result is not None
    assert result[0] > result[1]


def test_xg_from_event_no_data():
    assert xg_from_event({}) is None
