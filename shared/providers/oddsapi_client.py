from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ── key rotation ─────────────────────────────────────────────────────────────
_keys: List[Tuple[int, str]] = []
_keys_loaded = False

def _load_keys() -> None:
    global _keys, _keys_loaded
    if _keys_loaded:
        return
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
    raw = os.getenv("ODDS_API_KEYS", "") or os.getenv("ODDSAPI_KEY", "")
    candidates = [k.strip() for k in raw.replace(",", "\n").splitlines() if k.strip()]
    _keys = [(500, k) for k in candidates]
    _keys.sort(key=lambda x: -x[0])
    _keys_loaded = True

def _best_key() -> Optional[str]:
    _load_keys()
    for remaining, key in _keys:
        if remaining > 0:
            return key
    return None

def _update_remaining(used_key: str, remaining: int) -> None:
    global _keys
    _keys = [(remaining if k == used_key else r, k) for r, k in _keys]
    _keys.sort(key=lambda x: -x[0])

def _exhaust_key(used_key: str) -> None:
    _update_remaining(used_key, 0)

# ── real API call ─────────────────────────────────────────────────────────────
BASE_URL = "https://api.the-odds-api.com/v4"

def _get(path: str, params: Dict[str, str], _tried: int = 0) -> Tuple[Any, int]:
    key = _best_key()
    if key is None:
        raise RuntimeError("No Odds-API keys with remaining requests available")
    qs = "&".join(f"{k}={v}" for k, v in {**params, "apiKey": key}.items())
    url = f"{BASE_URL}/{path}?{qs}"
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            remaining = int(r.headers.get("x-requests-remaining", "0"))
            _update_remaining(key, remaining)
            return json.loads(r.read()), remaining
    except urllib.error.HTTPError as e:
        if e.code in (401, 422, 429):
            _exhaust_key(key)
            if _tried < 10:
                return _get(path, params, _tried + 1)
            raise RuntimeError(f"All keys failed (last HTTP {e.code})")
        raise

# ── sport groups ──────────────────────────────────────────────────────────────
SPORT_GROUP: Dict[str, List[str]] = {
    "basket": ["basketball_nba", "basketball_euroleague", "basketball_wnba"],
    "futbol": ["soccer_epl", "soccer_spain_la_liga", "soccer_uefa_champs_league", "soccer_usa_mls"],
    "tenis":  ["tennis_atp_italian_open", "tennis_wta_italian_open"],
}

def _normalize_event(raw: Dict[str, Any], sport_key: str) -> Dict[str, Any]:
    bookmakers = raw.get("bookmakers", [])
    odds_h2h: Dict[str, float] = {}
    for bm in bookmakers[:3]:
        for mkt in bm.get("markets", []):
            if mkt.get("key") == "h2h":
                for outcome in mkt.get("outcomes", []):
                    odds_h2h[outcome["name"]] = outcome["price"]
    return {
        "id": raw.get("id", ""),
        "datetime": raw.get("commence_time", ""),
        "title": raw.get("away_team", "?") + " vs " + raw.get("home_team", "?"),
        "home_team": raw.get("home_team", ""),
        "away_team": raw.get("away_team", ""),
        "league": raw.get("sport_title", sport_key),
        "status": "Pendiente",
        "odds": odds_h2h,
        "_source": "oddsapi",
        "_sport_key": sport_key,
    }

def fetch_fixtures(sport_key: str) -> List[Dict[str, Any]]:
    """Fetch upcoming events for sport_key. Returns [] on any error."""
    try:
        data, _ = _get(
            f"sports/{sport_key}/odds",
            {"regions": "eu,uk,us", "markets": "h2h", "oddsFormat": "decimal", "dateFormat": "iso"},
        )
        return [_normalize_event(ev, sport_key) for ev in data]
    except Exception as exc:
        import sys
        print(f"[oddsapi_client] fetch_fixtures({sport_key}) failed: {exc}", file=sys.stderr)
        return []

def fetch_sport_group(group: str) -> List[Dict[str, Any]]:
    """Fetch all sport_keys for group: basket / futbol / tenis."""
    results: List[Dict[str, Any]] = []
    for sk in SPORT_GROUP.get(group, []):
        results.extend(fetch_fixtures(sk))
    return results
