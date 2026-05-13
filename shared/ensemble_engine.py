"""
Ensemble Engine: combina múltiples modelos por deporte con pesos configurables.
Evita depender de un solo modelo frágil.
SCRIPT_OK
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ModelOutput:
    model_name: str
    prob_home: float
    prob_draw: float
    prob_away: float
    confidence: float = 1.0
    metadata: dict = field(default_factory=dict)


@dataclass
class EnsembleResult:
    prob_home: float
    prob_draw: float
    prob_away: float
    models_used: list[str]
    weights_applied: dict[str, float]


def _normalize(prob_home: float, prob_draw: float, prob_away: float) -> tuple[float, float, float]:
    total = prob_home + prob_draw + prob_away
    if total <= 0:
        return (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0)
    return (
        prob_home / total,
        prob_draw / total,
        prob_away / total,
    )


def weighted_ensemble(
    outputs: list[ModelOutput],
    custom_weights: Optional[dict[str, float]] = None,
) -> EnsembleResult:
    if not outputs:
        raise ValueError("Se requiere al menos un ModelOutput")

    weights: dict[str, float] = {}
    for output in outputs:
        if custom_weights is not None:
            base_weight = custom_weights.get(output.model_name, output.confidence)
        else:
            base_weight = output.confidence
        weights[output.model_name] = max(float(base_weight), 0.0)

    total_weight = sum(weights.values())
    if total_weight <= 0:
        weights = {output.model_name: 1.0 for output in outputs}
        total_weight = float(len(outputs))

    prob_home = 0.0
    prob_draw = 0.0
    prob_away = 0.0

    for output in outputs:
        weight = weights[output.model_name] / total_weight
        prob_home += weight * output.prob_home
        prob_draw += weight * output.prob_draw
        prob_away += weight * output.prob_away

    prob_home, prob_draw, prob_away = _normalize(prob_home, prob_draw, prob_away)

    return EnsembleResult(
        prob_home=round(prob_home, 4),
        prob_draw=round(prob_draw, 4),
        prob_away=round(prob_away, 4),
        models_used=[output.model_name for output in outputs],
        weights_applied={name: round(weight / total_weight, 4) for name, weight in weights.items()},
    )


SPORT_DEFAULT_WEIGHTS = {
    "futbol": {
        "poisson": 0.5,
        "monte_carlo": 0.3,
        "edge_simple": 0.2,
    },
    "tenis": {
        "elo_surface": 0.6,
        "monte_carlo": 0.25,
        "edge_simple": 0.15,
    },
    "basket": {
        "net_rating": 0.5,
        "monte_carlo": 0.35,
        "edge_simple": 0.15,
    },
}


def get_sport_weights(sport: str) -> dict[str, float]:
    return SPORT_DEFAULT_WEIGHTS.get(sport, {"edge_simple": 1.0})

if __name__ == "__main__":
    print("SCRIPT OK")
