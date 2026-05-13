from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

UTC = timezone.utc


def _norm_odds_tennis(ev: dict[str, Any], sport_key: str, title: str) -> dict[str, Any]:
    home = ev.get("home_team", "TBD")
    away = ev.get("away_team", "TBD")
    start_time = ev.get("commence_time", datetime.now(UTC).isoformat())
    fixture_id = str(ev.get("id") or f"{home}-{away}-{start_time}")
    return {
        "fixture_id": fixture_id,
        "sport": "tenis",
        "league": title,
        "home": home,
        "away": away,
        "start_time": start_time,
        "status": "scheduled",
        "source": "oddsapi",
        "markets": [],
        "raw": {"sport_key": sport_key},
    }


def fetch_tennis_events() -> list[dict[str, Any]]:
    from shared.providers.oddsapi_client import _get
    import sys

    # 1. Obtener torneos activos de tenis
    try:
        sports_data, _ = _get("sports", {"all": "false"})
    except Exception as exc:
        print(f"[tenis_provider] error obteniendo sports: {exc}", file=sys.stderr)
        return []

    active_tennis = [
        s for s in sports_data
        if "tennis" in s.get("key", "").lower() and s.get("active", False)
    ]

    if not active_tennis:
        print("[tenis_provider] sin torneos de tenis activos", file=sys.stderr)
        return []

    # 2. Obtener eventos de cada torneo activo
    results = []
    for sport in active_tennis:
        sport_key = sport["key"]
        title = sport.get("title", sport_key)
        try:
            data, _ = _get(
                f"sports/{sport_key}/events",
                {"dateFormat": "iso"},
            )
            if isinstance(data, list):
                for ev in data:
                    results.append(_norm_odds_tennis(ev, sport_key, title))
        except Exception as exc:
            print(f"[tenis_provider] {sport_key}: {exc}", file=sys.stderr)
            continue

    return results

if __name__ == "__main__":
    print("SCRIPT OK")
