from __future__ import annotations

import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE = "https://api.balldontlie.io"
API_KEY = (os.getenv("BALLDONTLIE_API_KEY") or "").strip()

def _headers() -> dict[str, str]:
    if not API_KEY:
        raise RuntimeError("Falta BALLDONTLIE_API_KEY en .env")
    return {"Authorization": API_KEY}

def get_nba_odds_by_date(date_str: str):
    url = f"{BASE}/nba/v1/odds"
    r = requests.get(url, headers=_headers(), params={"dates[]": date_str}, timeout=30)
    r.raise_for_status()
    return r.json()
