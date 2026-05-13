from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

UTC = timezone.utc

# Ligas a consultar — agrupadas por región
SOCCER_LEAGUES = [
    # Europa Top
    "soccer_epl",
    "soccer_spain_la_liga",
    "soccer_germany_bundesliga",
    "soccer_italy_serie_a",
    "soccer_france_ligue_one",
    "soccer_netherlands_eredivisie",
    "soccer_portugal_primeira_liga",
    # Copas Europa
    "soccer_uefa_champs_league",
    "soccer_uefa_europa_league",
    "soccer_uefa_europa_conference_league",
    # Latinoamérica
    "soccer_brazil_campeonato",
    "soccer_argentina_primera_division",
    "soccer_mexico_ligamx",
    "soccer_colombia_primera_a",
    "soccer_ecuador_liga_pro",
    "soccer_conmebol_copa_libertadores",
    "soccer_conmebol_copa_sudamericana",
    "soccer_usa_mls",
]

LEAGUE_NAMES = {
    "soccer_epl":                          "Premier League",
    "soccer_spain_la_liga":                "La Liga",
    "soccer_germany_bundesliga":           "Bundesliga",
    "soccer_italy_serie_a":                "Serie A",
    "soccer_france_ligue_one":             "Ligue 1",
    "soccer_netherlands_eredivisie":       "Eredivisie",
    "soccer_portugal_primeira_liga":       "Primeira Liga",
    "soccer_uefa_champs_league":           "Champions League",
    "soccer_uefa_europa_league":           "Europa League",
    "soccer_uefa_europa_conference_league":"Conference League",
    "soccer_brazil_campeonato":            "Série A Brasil",
    "soccer_argentina_primera_division":   "Primera División",
    "soccer_mexico_ligamx":                "Liga MX",
    "soccer_colombia_primera_a":           "Primera A",
    "soccer_ecuador_liga_pro":             "LigaPro Ecuador",
    "soccer_conmebol_copa_libertadores":   "Copa Libertadores",
    "soccer_conmebol_copa_sudamericana":   "Copa Sudamericana",
    "soccer_usa_mls":                      "MLS",
}


def _norm_odds_event(ev: dict[str, Any], sport_key: str) -> dict[str, Any]:
    home = ev.get("home_team", "TBD")
    away = ev.get("away_team", "TBD")
    start_time = ev.get("commence_time", datetime.now(UTC).isoformat())
    fixture_id = str(ev.get("id") or f"{home}-{away}-{start_time}")
    league = LEAGUE_NAMES.get(sport_key, sport_key)
    return {
        "fixture_id": fixture_id,
        "sport": "futbol",
        "league": league,
        "sport_key": sport_key,
        "home": home,
        "away": away,
        "start_time": start_time,
        "status": "scheduled",
        "source": "oddsapi",
        "markets": ev.get("bookmakers", []),
        "raw": {},
    }


# Ligas sin soporte en the-odds-api — pendiente API-Football RapidHub plan paid
_UNSUPPORTED_ODDS = {"soccer_colombia_primera_a", "soccer_ecuador_liga_pro"}


def fetch_futbol_events() -> list[dict[str, Any]]:
    from shared.providers.oddsapi_client import _get
    import sys
    results = []
    for sport_key in SOCCER_LEAGUES:
        if sport_key in _UNSUPPORTED_ODDS:
            print(f"[futbol_provider] {sport_key}: pendiente API-Football (requiere plan paid)", file=sys.stderr)
            continue
        try:
            data, _ = _get(
                f"sports/{sport_key}/events",
                {"dateFormat": "iso", "eventIds": ""},
            )
            if isinstance(data, list):
                for ev in data:
                    results.append(_norm_odds_event(ev, sport_key))
        except Exception as exc:
            print(f"[futbol_provider] {sport_key}: {exc}", file=sys.stderr)
            continue
    return results

if __name__ == "__main__":
    print("SCRIPT OK")
