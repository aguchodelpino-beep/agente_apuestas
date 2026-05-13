from departments.deportes.tenis.elo_model import (
    EloStore,
    expected_score,
    update_ratings,
    win_probability,
)


def test_expected_score_equal_ratings():
    assert abs(expected_score(1500, 1500) - 0.5) < 1e-9


def test_expected_score_higher_wins_more():
    assert expected_score(1600, 1400) > 0.7


def test_update_increases_winner_rating():
    store = EloStore()
    update_ratings(store, "Djokovic", "Nadal")
    assert store.get("Djokovic") > 1500
    assert store.get("Nadal") < 1500


def test_surface_elo_independent():
    store = EloStore()
    update_ratings(store, "Nadal", "Djokovic", surface="clay")
    assert store.get("Nadal", "clay") > 1500
    assert store.get("Djokovic", "clay") < 1500
    assert store.get("Nadal") > 1500


def test_win_probability_sums_to_one():
    store = EloStore()
    update_ratings(store, "Federer", "Murray", surface="grass")
    pa, pb = win_probability(store, "Federer", "Murray", surface="grass")
    assert abs(pa + pb - 1.0) < 1e-6


def test_default_prob_is_50_50():
    store = EloStore()
    pa, pb = win_probability(store, "A", "B")
    assert pa == 0.5
    assert pb == 0.5
