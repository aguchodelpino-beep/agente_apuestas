from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from shared.providers.provider_utils import safe_get_json, normalize_status

UTC = timezone.utc

def _norm_tennis_event(ev: dict[str, Any]) -> dict[str, Any]:
    comp = ev.get("competitions", [{}])[0]
    competitors = comp.get("competitors", [])
    home = competitors[0].get("athlete", {}).get("displayName") if len(competitors) > 0 else "TBD"
    away = competitors[1].get("athlete", {}).get("displayName") if len(competitors) > 1 else "TBD"
    status = normalize_status(ev.get("status", {}).get("type", {}).get("state"))
    league = ev.get("league", {}).get("name") or comp.get("league", {}).get("name") or "Tennis"
    start_time = ev.get("date") or datetime.now(UTC).isoformat()
    fixture_id = str(ev.get("id") or f"{home}-{away}-{start_time}")
    return {
        "fixture_id": fixture_id,
        "sport": "tenis",
        "league": league,
        "home": home,
        "away": away,
        "start_time": start_time,
        "status": status,
        "source": "espn",
        "markets": [],
        "raw": {
            "shortName": ev.get("shortName"),
            "status_detail": ev.get("status", {}).get("type", {}).get("description"),
        },
    }

def fetch_tennis_events() -> list[dict[str, Any]]:
    url = "https://site.api.espn.com/apis/site/v2/sports/tennis/atp/scoreboard"
    data = safe_get_json(url)
    events = data.get("events", []) or []
    return [_norm_tennis_event(ev) for ev in events]
