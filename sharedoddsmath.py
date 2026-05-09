from __future__ import annotations

def american_to_prob(odds: int | float) -> float:
    odds = float(odds)
    if odds == 0:
        return 0.0
    if odds > 0:
        return 100.0 / (odds + 100.0)
    return abs(odds) / (abs(odds) + 100.0)


def edge_percent(model_prob: float, implied_prob: float) -> float:
    return float(model_prob) - float(implied_prob)
