from __future__ import annotations

from typing import Any

from shared.provider_balldontlie_stats import nba_get_games_by_date


def _safe_list(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = data.get("data", [])
    return rows if isinstance(rows, list) else []


def format_nba_games(date_str: str) -> str:
    rows = _safe_list(nba_get_games_by_date(date_str))
    if not rows:
        return f"🏀 *NBA JUEGOS*\n\nSin juegos para {date_str}."

    lines = [f"🏀 *NBA JUEGOS*", f"", f"Fecha: `{date_str}`", ""]
    for row in rows[:15]:
        home = row.get("home_team", {}) or {}
        away = row.get("visitor_team", {}) or {}
        status = row.get("status") or "N/A"
        home_name = home.get("full_name") or home.get("name") or "Home"
        away_name = away.get("full_name") or away.get("name") or "Away"
        lines.append(f"• {away_name} vs {home_name} — {status}")
    return "\n".join(lines)
