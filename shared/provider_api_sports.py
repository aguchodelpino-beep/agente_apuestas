from __future__ import annotations
import requests
from typing import Any, Dict, List, Optional
from shared.providers import API_SPORTS_KEY

BASE_URL = "https://v3.football.api-sports.io"

def _headers() -> dict:
    return {
        "x-apisports-key": API_SPORTS_KEY,
    }

def api_sports_get(path: str, params: Optional[dict] = None, timeout: int = 20) -> Dict[str, Any]:
    if not API_SPORTS_KEY:
        raise RuntimeError("API_SPORTS_KEY no configurada")

    url = f"{BASE_URL}{path}"
    r = requests.get(url, headers=_headers(), params=params or {}, timeout=timeout)

    try:
        data = r.json()
    except Exception:
        data = {"raw_text": r.text[:500]}

    return {
        "status_code": r.status_code,
        "url": r.url,
        "data": data,
        "headers": dict(r.headers),
    }

def get_status() -> Dict[str, Any]:
    return api_sports_get("/status")

def get_leagues(
    season: Optional[int] = None,
    country: Optional[str] = None,
    search: Optional[str] = None,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    if season is not None:
        params["season"] = season
    if country:
        params["country"] = country
    if search:
        params["search"] = search
    return api_sports_get("/leagues", params=params)

def get_fixtures(
    league: int,
    season: int,
    date: Optional[str] = None,
    next_n: Optional[int] = None,
    last_n: Optional[int] = None,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {
        "league": league,
        "season": season,
    }
    if date:
        params["date"] = date
    if next_n is not None:
        params["next"] = next_n
    if last_n is not None:
        params["last"] = last_n
    return api_sports_get("/fixtures", params=params)

def extract_response_items(payload: Dict[str, Any]) -> List[dict]:
    data = payload.get("data", {})
    response = data.get("response", []) if isinstance(data, dict) else []
    if isinstance(response, list):
        return response
    return []

def find_league_id_by_name(search_text: str, country: Optional[str] = None) -> List[dict]:
    payload = get_leagues(search=search_text)
    items = extract_response_items(payload)
    out: List[dict] = []

    for item in items:
        league = item.get("league", {})
        country_obj = item.get("country", {})
        row = {
            "league_id": league.get("id"),
            "league_name": league.get("name"),
            "league_type": league.get("type"),
            "country": country_obj.get("name"),
            "country_code": country_obj.get("code"),
        }
        if country and str(row["country"]).lower() != country.lower():
            continue
        out.append(row)

    return out

def list_fixtures_by_league(league: int, season: int, next_n: Optional[int] = None, last_n: Optional[int] = None) -> List[dict]:
    payload = get_fixtures(league=league, season=season, next_n=next_n, last_n=last_n)
    items = extract_response_items(payload)
    out: List[dict] = []

    for item in items:
        fixture = item.get("fixture", {})
        league_obj = item.get("league", {})
        teams = item.get("teams", {})
        out.append({
            "fixture_id": fixture.get("id"),
            "date": fixture.get("date"),
            "timestamp": fixture.get("timestamp"),
            "status": (fixture.get("status", {}) or {}).get("short"),
            "league_id": league_obj.get("id"),
            "league_name": league_obj.get("name"),
            "country": league_obj.get("country"),
            "home": (teams.get("home", {}) or {}).get("name"),
            "away": (teams.get("away", {}) or {}).get("name"),
        })

    return out

if __name__ == "__main__":
    print("SCRIPT OK")
