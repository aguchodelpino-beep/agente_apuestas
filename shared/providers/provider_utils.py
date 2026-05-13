from __future__ import annotations

from typing import Any


def get_json(url: str, *, timeout: int = 10, headers: dict | None = None, **kwargs):
    import requests
    try:
        r = requests.get(url, headers=headers or {}, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}


def safe_get_json(url: str, *, timeout: int = 10, headers: dict | None = None, **kwargs):
    import requests
    try:
        r = requests.get(url, headers=headers or {}, timeout=timeout)
        if r.status_code == 200:
            return r.json()
        return {}
    except Exception:
        return {}


def env(*args, **kwargs):
    return None


def normalize_status(value):
    if isinstance(value, dict):
        return value.get("statusName") or value.get("name") or ""
    return value


def merge_by_fixture_id(existing: list[dict[str, Any]], incoming: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}

    for item in existing:
        fixture_id = str(item.get("fixture_id") or item.get("fixtureId") or "").strip()
        if fixture_id:
            merged[fixture_id] = dict(item)

    for item in incoming:
        fixture_id = str(item.get("fixture_id") or item.get("fixtureId") or "").strip()
        if not fixture_id:
            continue
        previous = merged.get(fixture_id, {})
        merged[fixture_id] = {**previous, **item}

    return list(merged.values())


def normalize_fixture_row(item: dict[str, Any], *, sport_name: str, time_field: str) -> dict[str, Any]:
    participants = item.get("participants") or {}
    if isinstance(participants, list):
        home = participants[0].get("name", "") if len(participants) > 0 and isinstance(participants[0], dict) else ""
        away = participants[1].get("name", "") if len(participants) > 1 and isinstance(participants[1], dict) else ""
    else:
        home = participants.get("participant1Name") or item.get("home", "")
        away = participants.get("participant2Name") or item.get("away", "")

    sport = item.get("sport") or {}
    tournament = item.get("tournament") or {}
    status = item.get("status")

    return {
        "fixture_id": item.get("fixtureId") or item.get("fixture_id"),
        "sport": sport.get("sportName") if isinstance(sport, dict) else (sport or sport_name),
        "league": tournament.get("tournamentName") if isinstance(tournament, dict) else item.get("league", ""),
        "home": home,
        "away": away,
        "status": normalize_status(status),
        "live": status.get("live") if isinstance(status, dict) else item.get("live", False),
        time_field: item.get("startDate") or item.get(time_field, ""),
        "raw": item,
    }

if __name__ == "__main__":
    print("SCRIPT OK")
