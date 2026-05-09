from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from shared.providers.provider_utils import safe_get_json, normalize_status

UTC = timezone.utc

def _norm_soccer_event(ev: dict[str, Any]) -> dict[str, Any]:
    home = ev.get("team1", {}).get("teamName") or ev.get("team1", {}).get("teamNameShort") or "TBD"
    away = ev.get("team2", {}).get("teamName") or ev.get("team2", {}).get("teamNameShort") or "TBD"
    league = ev.get("leagueShortcut") or ev.get("leagueName") or "Soccer"
    start_time = ev.get("matchDateTime") or datetime.now(UTC).isoformat()
    status = normalize_status(ev.get("matchIsFinished") and "finished" or "scheduled")
    fixture_id = str(ev.get("matchID") or f"{home}-{away}-{start_time}")
    return {
        "fixture_id": fixture_id,
        "sport": "futbol",
        "league": league,
        "home": home,
        "away": away,
        "start_time": start_time,
        "status": status,
        "source": "openligadb",
        "markets": [],
        "raw": {
            "group": ev.get("group", {}),
            "location": ev.get("location", {}),
        },
    }

def fetch_futbol_events() -> list[dict[str, Any]]:
    url = "https://api.openligadb.de/getmatchdata/bl1"
    data = safe_get_json(url)
    if not isinstance(data, list):
        return []
    return [_norm_soccer_event(ev) for ev in data]
