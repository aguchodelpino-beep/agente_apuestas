from __future__ import annotations

from typing import Any, Union

Number = Union[int, float]


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"valor inválido para odds/probabilidad: {value!r}")


def american_to_prob(odds: Number) -> float:
    odds = _to_float(odds)
    if odds == 0:
        raise ValueError("american odds no puede ser 0")
    if odds < 0:
        return abs(odds) / (abs(odds) + 100.0)
    return 100.0 / (odds + 100.0)


def decimal_to_prob(decimal_odds: Number) -> float:
    decimal_odds = _to_float(decimal_odds)
    if decimal_odds <= 1.0:
        raise ValueError("decimal odds debe ser > 1")
    return 1.0 / decimal_odds


def prob_to_decimal(prob: Number) -> float:
    prob = _to_float(prob)
    if prob <= 0.0 or prob >= 1.0:
        raise ValueError("prob debe estar entre 0 y 1")
    return 1.0 / prob


def prob_to_american(prob: Number) -> int:
    prob = _to_float(prob)
    if prob <= 0.0 or prob >= 1.0:
        raise ValueError("prob debe estar entre 0 y 1")
    if prob >= 0.5:
        return int(round(-(prob / (1.0 - prob)) * 100.0))
    return int(round(((1.0 - prob) / prob) * 100.0))


def american_to_decimal(odds: Number) -> float:
    odds = _to_float(odds)
    if odds == 0:
        raise ValueError("american odds no puede ser 0")
    if odds > 0:
        return 1.0 + (odds / 100.0)
    return 1.0 + (100.0 / abs(odds))


def decimal_to_american(decimal_odds: Number) -> int:
    decimal_odds = _to_float(decimal_odds)
    if decimal_odds <= 1.0:
        raise ValueError("decimal odds debe ser > 1")
    if decimal_odds >= 2.0:
        return int(round((decimal_odds - 1.0) * 100.0))
    return int(round(-100.0 / (decimal_odds - 1.0)))


def implied_probability(odds: Number) -> float:
    odds = _to_float(odds)
    if odds > 1.0:
        return decimal_to_prob(odds)
    if 0.0 < odds < 1.0:
        return odds
    return american_to_prob(odds)


def edge_percent(model_prob: Number, market_prob: Number) -> float:
    return (_to_float(model_prob) - _to_float(market_prob)) * 100.0


def edge_from_model(model_prob: Number, market_odds: Number) -> float:
    return _to_float(model_prob) - implied_probability(market_odds)


def expected_value(probability: Number, decimal_odds: Number, stake: Number = 1.0) -> float:
    p = _to_float(probability)
    d = _to_float(decimal_odds)
    s = _to_float(stake)
    if d <= 1.0:
        raise ValueError("decimal_odds debe ser > 1")
    return (p * d * s) - s


def kelly_fraction(model_prob: Number, decimal_odds: Number, fraction: Number = 1.0) -> float:
    p = _to_float(model_prob)
    d = _to_float(decimal_odds)
    f = _to_float(fraction)

    if not 0.0 <= p <= 1.0:
        raise ValueError("model_prob debe estar entre 0 y 1")
    if d <= 1.0:
        raise ValueError("decimal_odds debe ser > 1")

    b = d - 1.0
    q = 1.0 - p
    k = (b * p - q) / b
    return max(0.0, k * f)


# Aliases legacy / compatibilidad
americantoprob = american_to_prob
decimaltoprob = decimal_to_prob
edgepercent = edge_percent
kellyfraction = kelly_fraction
probtodecimal = prob_to_decimal
probtoamerican = prob_to_american
americantodecimal = american_to_decimal
decimaltoamerican = decimal_to_american
