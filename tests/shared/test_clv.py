import pytest
from shared.clv import calculate_clv_pct_decimal, enrich_pick_with_clv, PickContext


def test_calculate_clv_pct_decimal():
    assert calculate_clv_pct_decimal(2.0, 1.90) == pytest.approx(-5.0, abs=1e-4)
    assert calculate_clv_pct_decimal(2.0, 2.10) == pytest.approx(5.0, abs=1e-4)
    assert calculate_clv_pct_decimal(None, 1.90) is None
    assert calculate_clv_pct_decimal(2.0, None) is None


def test_enrich_pick_with_clv():
    ctx = enrich_pick_with_clv(2.05, 1.95)
    assert isinstance(ctx, PickContext)
    assert ctx.opening_odds == 2.05
    assert ctx.closing_odds == 1.95
    assert ctx.clv_pct == pytest.approx(-4.878049, abs=1e-4)


def test_pick_context_describe():
    txt = enrich_pick_with_clv(2.05, 1.95).describe()
    assert "CLV" in txt
    assert "bajó de 2.05 → 1.95" in txt
