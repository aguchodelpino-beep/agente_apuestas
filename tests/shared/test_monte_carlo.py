from shared.monte_carlo import run_football_monte_carlo, run_basketball_monte_carlo


def test_football_probs_sum_to_one():
    r = run_football_monte_carlo(1.5, 1.1, n_sims=5000, seed=42)
    total = r.home_win_pct + r.draw_pct + r.away_win_pct
    assert abs(total - 1.0) < 0.02


def test_football_strong_home():
    r = run_football_monte_carlo(3.0, 0.3, n_sims=5000, seed=42)
    assert r.home_win_pct > 0.75


def test_football_over_under_reasonable():
    r = run_football_monte_carlo(1.5, 1.5, n_sims=5000, seed=42)
    assert 0.4 < r.over_2_5_pct < 0.7


def test_football_mean_total_approx_xg():
    r = run_football_monte_carlo(1.5, 1.0, n_sims=10000, seed=7)
    assert abs(r.mean_total_goals - 2.5) < 0.2


def test_basketball_probs_sum_to_one():
    r = run_basketball_monte_carlo(0.6, 220.0, spread=5.0, n_sims=5000, seed=42)
    assert abs(r["home_win_pct"] + r["away_win_pct"] - 1.0) < 0.02


def test_basketball_over_under_complement():
    r = run_basketball_monte_carlo(0.55, 215.0, n_sims=5000, seed=42)
    assert abs(r["over_pct"] + r["under_pct"] - 1.0) < 0.02
