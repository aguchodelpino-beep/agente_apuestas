from __future__ import annotations
import requests
from typing import Any, Dict, Optional
from core.config import Config

BASE_URL = "https://api.sportsgameodds.com/v2"

def headers() -> dict:
    return {
        "x-api-key": Config.SPORTSGAME_ODDS_KEY,
        "Accept": "application/json",
    }

def get_events(
    league_id: str,
    params: Optional[dict] = None,
    timeout: int = 20
) -> Dict[str, Any]:
    if not Config.SPORTSGAME_ODDS_KEY:
        raise RuntimeError("SPORTSGAME_ODDS_KEY no configurada")
    
    url = f"{BASE_URL}/events"
    params = params or {"oddsAvailable": "true", "limit": 50}
    params["leagueID"] = league_id
    
    r = requests.get(url, headers=headers(), params=params, timeout=timeout)
    
    try:
        data = r.json()
    except Exception:
        data = {"raw_text": r.text[:1000]}
    
    return {
        "status_code": r.status_code,
        "url": r.url,
        "data": data,
        "headers": dict(r.headers),
    }

def get_sports(timeout: int = 10) -> Dict[str, Any]:
    r = requests.get("https://api.sportsgameodds.com/sports", headers=headers(), timeout=timeout)
    try:
        return r.json()
    except:
        return {"raw_text": r.text[:1000]}

def get_leagues(timeout: int = 10) -> Dict[str, Any]:
    r = requests.get("https://api.sportsgameodds.com/leagues", headers=headers(), timeout=timeout)
    try:
        return r.json()
    except:
        return {"raw_text": r.text[:1000]}

if __name__ == "__main__":
    print("SCRIPT OK")
