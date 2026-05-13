"""
Modelo Elo para tenis con ajuste por superficie.
SCRIPT_OK
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

SURFACES = ("clay", "grass", "hard", "carpet")
K_FACTOR = 32.0
SURFACE_WEIGHT = 0.4


@dataclass
class EloStore:
    general: dict[str, float] = field(default_factory=dict)
    surface: dict[str, dict[str, float]] = field(default_factory=dict)
    default_rating: float = 1500.0

    def get(self, player: str, surface: Optional[str] = None) -> float:
        if surface and surface in SURFACES:
            return self.surface.get(player, {}).get(surface, self.default_rating)
        return self.general.get(player, self.default_rating)

    def set(self, player: str, rating: float, surface: Optional[str] = None) -> None:
        if surface and surface in SURFACES:
            if player not in self.surface:
                self.surface[player] = {}
            self.surface[player][surface] = rating
        else:
            self.general[player] = rating


def expected_score(rating_a: float, rating_b: float) -> float:
    return 1.0 / (1.0 + math.pow(10, (rating_b - rating_a) / 400.0))


def update_ratings(
    store: EloStore,
    winner: str,
    loser: str,
    surface: Optional[str] = None,
) -> tuple[float, float]:
    winner_general = store.get(winner)
    loser_general = store.get(loser)

    exp_w = expected_score(winner_general, loser_general)
    new_winner_general = winner_general + K_FACTOR * (1.0 - exp_w)
    new_loser_general = loser_general + K_FACTOR * (0.0 - (1.0 - exp_w))

    store.set(winner, new_winner_general)
    store.set(loser, new_loser_general)

    if surface and surface in SURFACES:
        winner_surface = store.get(winner, surface)
        loser_surface = store.get(loser, surface)

        exp_ws = expected_score(winner_surface, loser_surface)
        new_winner_surface = winner_surface + K_FACTOR * (1.0 - exp_ws)
        new_loser_surface = loser_surface + K_FACTOR * (0.0 - (1.0 - exp_ws))

        store.set(winner, new_winner_surface, surface)
        store.set(loser, new_loser_surface, surface)

    return store.get(winner), store.get(loser)


def win_probability(
    store: EloStore,
    player_a: str,
    player_b: str,
    surface: Optional[str] = None,
) -> tuple[float, float]:
    gen_a = store.get(player_a)
    gen_b = store.get(player_b)

    if surface and surface in SURFACES:
        surf_a = store.get(player_a, surface)
        surf_b = store.get(player_b, surface)
        blended_a = (1 - SURFACE_WEIGHT) * gen_a + SURFACE_WEIGHT * surf_a
        blended_b = (1 - SURFACE_WEIGHT) * gen_b + SURFACE_WEIGHT * surf_b
    else:
        blended_a = gen_a
        blended_b = gen_b

    prob_a = expected_score(blended_a, blended_b)
    return round(prob_a, 4), round(1.0 - prob_a, 4)


_default_store = EloStore()


def get_default_store() -> EloStore:
    return _default_store


def reset_store() -> None:
    global _default_store
    _default_store = EloStore()

if __name__ == "__main__":
    print("SCRIPT OK")
