from __future__ import annotations

from departments.analitica.deportes.futbol.service import build_futbol_pick_messages


def handle_futbol_picks_analitica(*args, **kwargs) -> str:
    bankroll = 1000.0
    model_name = "poisson_match_v1"
    model_version = "2026.05"

    lines = build_futbol_pick_messages(
        bankroll=bankroll,
        model_name=model_name,
        model_version=model_version,
    )
    return "\n".join(lines)
