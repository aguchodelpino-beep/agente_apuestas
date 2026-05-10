from __future__ import annotations

from typing import Any


def handle_tenis_picks_analitica(*args, **kwargs) -> str:
    try:
        from departments.analitica.deportes.tenis.service import build_tenis_pick_messages

        # 1. banco de pruebas; tú lo puedes parametrizar o leer de config
        bankroll = 1000.0
        model_name = "elo_surface_v1"
        model_version = "2026.05"

        lines = build_tenis_pick_messages(
            bankroll=bankroll,
            model_name=model_name,
            model_version=model_version,
        )
        return "\n".join(lines)

    except Exception as e:
        return f"🎾 TENIS PICKS\n\nError al procesar picks: {e}"
