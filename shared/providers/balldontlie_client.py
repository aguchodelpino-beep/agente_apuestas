from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

BASE = "https://api.balldontlie.io/v1"

def _key() -> str:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
    return os.getenv("BALLDONTLIE_API_KEY", "")

def _get(path: str, params: Dict[str, str]) -> Any:
    key = _key()
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{BASE}/{path}?{qs}"
    req = urllib.request.Request(url, headers={"Authorization": key})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        import sys
        print(f"[balldontlie] {path} HTTP {e.code}", file=sys.stderr)
        return {}

def fetch_fixtures(sport_key: str = "basketball_nba") -> List[Dict[str, Any]]:
    """Fetch NBA games for today and next 3 days."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    data = _get("games", {"dates[]": today, "per_page": "20"})
    games = data.get("data", [])
    result = []
    for g in games:
        home = g.get("home_team", {})
        away = g.get("visitor_team", {})
        status = g.get("status", "")
        result.append({
            "id": str(g.get("id", "")),
            "datetime": g.get("date", ""),
            "title": f"{away.get('full_name','?')} vs {home.get('full_name','?')}",
            "home_team": home.get("full_name", ""),
            "away_team": away.get("full_name", ""),
            "league": "NBA",
            "status": status if status else "Scheduled",
            "odds": {},
            "_source": "balldontlie",
            "_sport_key": sport_key,
        })
    return result

if __name__ == "__main__":
    print("SCRIPT OK")
