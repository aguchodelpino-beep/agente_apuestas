from __future__ import annotations
import requests
from typing import Any, Dict, Optional
from core.config import Config

BASE_URL = "https://api.football-data.org/v4"

def _headers() -> dict:
    return {
        "X-Auth-Token": Config.FOOTBALL_DATA_KEY,
    }

def football_data_get(path: str, params: Optional[dict] = None, timeout: int = 20) -> Dict[str, Any]:
    if not Config.FOOTBALL_DATA_KEY:
        raise RuntimeError("FOOTBALL_DATA_KEY no configurada")

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

if __name__ == "__main__":
    print("SCRIPT OK")
