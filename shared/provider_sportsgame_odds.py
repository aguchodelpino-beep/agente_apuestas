from __future__ import annotations
import requests
from typing import Any, Dict, Optional
from core.config import Config

BASE_URL = "https://api.sportsgameodds.com"

def _headers() -> dict:
    return {
        "x-api-key": Config.SPORTSGAME_ODDS_KEY,
        "accept": "application/json",
    }

def sgo_get(path: str, params: Optional[dict] = None, timeout: int = 20) -> Dict[str, Any]:
    if not Config.SPORTSGAME_ODDS_KEY:
        raise RuntimeError("SPORTSGAME_ODDS_KEY no configurada")

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
