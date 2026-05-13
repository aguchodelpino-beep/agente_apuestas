from shared.market_models import (
    build_market_probs,
    prob_to_fair_odds,
    spread_prob,
    total_prob,
)


def test_fair_odds_roundtrip():
    assert abs((1 / prob_to_fair_odds(0.5)) - 0.5) < 1e-4


def test_spread_zero_preserves_prob():
    p_cover, p_no = spread_prob(0.6, spread_points=0.0)
    assert abs(p_cover - 0.6) < 0.05
    assert abs(p_cover + p_no - 1.0) < 1e-6


def test_spread_probs_sum_to_one():
    p1, p2 = spread_prob(0.6, 5.0)
    assert abs(p1 + p2 - 1.0) < 1e-6


def test_total_prob_at_line_equals_projected():
    over, under = total_prob(projected_total=220.0, line=220.0)
    assert abs(over - 0.5) < 0.02
    assert abs(over + under - 1.0) < 1e-6


def test_total_over_increases_with_higher_projection():
    over_hi, _ = total_prob(230.0, line=220.0)
    over_lo, _ = total_prob(210.0, line=220.0)
    assert over_hi > over_lo


def test_build_market_probs_returns_moneylines():
    mps = build_market_probs(
        0.5, 0.25, 0.25,
        projected_total=2.5,
        market_odds={"home": 2.0, "draw": 3.5, "away": 3.8},
        sport="futbol",
    )
    names = [m.market for m in mps]
    assert "moneyline_home" in names
    assert "moneyline_draw" in names
    assert "moneyline_away" in names


def test_edge_computed_correctly():
    mps = build_market_probs(
        0.6, 0.2, 0.2,
        projected_total=2.0,
        market_odds={"home": 1.5},
        sport="futbol",
    )
    home_mp = next(m for m in mps if m.market == "moneyline_home")
    assert abs(home_mp.edge - (0.6 - 1 / 1.5)) < 1e-3
