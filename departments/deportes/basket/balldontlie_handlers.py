from __future__ import annotations

from datetime import datetime

from departments.deportes.basket.balldontlie_service import format_nba_games


def handle_nbajuegos(date_str: str | None = None) -> str:
    if not date_str:
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
    return format_nba_games(date_str)
