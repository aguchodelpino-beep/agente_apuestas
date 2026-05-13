from __future__ import annotations
import requests
from typing import Any, Dict, Optional

BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"

def espn_get(path: str, params: Optional[dict] = None, timeout: int = 20) -> Dict[str, Any]:
    url = f"{BASE_URL}{path}"
    r = requests.get(url, params=params or {}, timeout=timeout)
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

def get_soccer_scoreboard(league: str = "eng.1", dates: Optional[str] = None) -> Dict[str, Any]:
    params = {}
    if dates:
        params["dates"] = dates
    return espn_get(f"/soccer/{league}/scoreboard", params=params)

def get_soccer_standings(league: str = "eng.1", season: Optional[int] = None) -> Dict[str, Any]:
    params = {}
    if season:
        params["season"] = season
    return espn_get(f"/soccer/{league}/standings", params=params)

def get_soccer_teams(league: str = "eng.1") -> Dict[str, Any]:
    return espn_get(f"/soccer/{league}/teams")

def get_nba_scoreboard(dates: Optional[str] = None) -> Dict[str, Any]:
    params = {}
    if dates:
        params["dates"] = dates
    return espn_get("/basketball/nba/scoreboard", params=params)

def get_nba_teams() -> Dict[str, Any]:
    return espn_get("/basketball/nba/teams")

def get_nba_news() -> Dict[str, Any]:
    return espn_get("/basketball/nba/news")

def get_tennis_scoreboard(dates: Optional[str] = None) -> Dict[str, Any]:
    params = {}
    if dates:
        params["dates"] = dates
    return espn_get("/tennis/atp/scoreboard", params=params)

def get_tennis_news() -> Dict[str, Any]:
    return espn_get("/tennis/atp/news")

def get_tennis_teams_like_listing() -> Dict[str, Any]:
    return espn_get("/tennis/atp/teams")

if __name__ == "__main__":
    print("SCRIPT OK")
