from __future__ import annotations

from departments.analitica.deportes.basket.service import build_basket_pick_messages


def handle_basket_picks_analitica(*args, **kwargs) -> str:
    bankroll = 1000.0
    model_name = "poisson_match_v1"
    model_version = "2026.05"

    lines = build_basket_pick_messages(
        bankroll=bankroll,
        model_name=model_name,
        model_version=model_version,
    )
    return "\n".join(lines)
