from __future__ import annotations

import json
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

BASE = "https://site.api.espn.com/apis/site/v2/sports"

SPORT_MAP: Dict[str, str] = {
    "basketball_nba":        "basketball/nba",
    "basketball_euroleague": "basketball/mens-college-basketball",
    "soccer_epl":            "soccer/eng.1",
    "soccer_spain_la_liga":  "soccer/esp.1",
    "soccer_uefa_champs_league": "soccer/uefa.champions",
    "soccer_usa_mls":        "soccer/usa.1",
    "tennis_atp_french_open":"tennis/atp",
    "tennis_wta_french_open":"tennis/wta",
}

GROUP_MAP: Dict[str, List[str]] = {
    "basket": ["basketball_nba"],
    "futbol": ["soccer_epl", "soccer_spain_la_liga", "soccer_uefa_champs_league"],
    "tenis":  ["tennis_atp_italian_open", "tennis_wta_italian_open"],
}

def _fetch(sport_path: str) -> List[Dict[str, Any]]:
    url = f"{BASE}/{sport_path}/scoreboard"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return json.loads(r.read()).get("events", [])
    except Exception as exc:
        import sys
        print(f"[espn_client] {sport_path} failed: {exc}", file=sys.stderr)
        return []

def _normalize(raw: Dict[str, Any], sport_key: str) -> Dict[str, Any]:
    comps = raw.get("competitions", [{}])[0]
    competitors = comps.get("competitors", [])
    home = next((c for c in competitors if c.get("homeAway") == "home"), {})
    away = next((c for c in competitors if c.get("homeAway") == "away"), {})
    home_name = home.get("team", {}).get("displayName", "?")
    away_name = away.get("team", {}).get("displayName", "?")

    # odds
    odds_raw = comps.get("odds", [{}])[0] if comps.get("odds") else {}
    espn_odds: Dict[str, Any] = {}
    if odds_raw:
        espn_odds = {
            "spread": odds_raw.get("spread"),
            "over_under": odds_raw.get("overUnder"),
            "home_ml": odds_raw.get("homeTeamOdds", {}).get("moneyLine"),
            "away_ml": odds_raw.get("awayTeamOdds", {}).get("moneyLine"),
        }

    status = raw.get("status", {}).get("type", {}).get("description", "Pendiente")
    return {
        "id": raw.get("id", ""),
        "datetime": raw.get("date", ""),
        "title": f"{away_name} vs {home_name}",
        "home_team": home_name,
        "away_team": away_name,
        "league": raw.get("season", {}).get("slug", sport_key),
        "status": status,
        "espn_odds": espn_odds,
        "_source": "espn",
        "_sport_key": sport_key,
    }

def fetch_fixtures(sport_key: str) -> List[Dict[str, Any]]:
    path = SPORT_MAP.get(sport_key)
    if not path:
        return []
    events = _fetch(path)
    return [_normalize(ev, sport_key) for ev in events]

def fetch_sport_group(group: str) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for sk in GROUP_MAP.get(group, []):
        results.extend(fetch_fixtures(sk))
    return results

def crosscheck(
    oddsapi_events: List[Dict[str, Any]],
    espn_events: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Enriquece eventos de Odds-API con datos ESPN cuando hay match por equipos.
    Retorna la lista de Odds-API con campo espn_match agregado.
    """
    enriched = []
    for ev in oddsapi_events:
        home = ev.get("home_team", "").lower()
        away = ev.get("away_team", "").lower()
        match = None
        for esp in espn_events:
            esp_home = esp.get("home_team", "").lower()
            esp_away = esp.get("away_team", "").lower()
            if (home in esp_home or esp_home in home) and (away in esp_away or esp_away in away):
                match = {
                    "espn_id": esp.get("id"),
                    "espn_status": esp.get("status"),
                    "espn_odds": esp.get("espn_odds", {}),
                }
                break
        ev["espn_match"] = match
        enriched.append(ev)
    return enriched
