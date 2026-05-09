import pytest

from shared.odds import (
    american_to_prob,
    decimal_to_prob,
    edge_percent,
    kelly_fraction,
    prob_to_decimal,
)


def test_decimal_prob_roundtrip():
    assert decimal_to_prob(2.0) == pytest.approx(0.5)
    assert prob_to_decimal(0.5) == pytest.approx(2.0)


def test_kelly_fraction_positive():
    assert kelly_fraction(0.55, 2.10) > 0


def test_american_and_edge():
    assert american_to_prob(-150) == pytest.approx(0.6)
    assert edge_percent(0.55, 0.50) == pytest.approx(5.0)
