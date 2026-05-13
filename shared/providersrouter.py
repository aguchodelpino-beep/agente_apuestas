from __future__ import annotations
from typing import List, Dict, Any

try:
    from shared.providers.oddsapi_client import fetch_fixtures as oddsapi_fetch
    HAS_ODDSAPI = True
except ImportError:
    HAS_ODDSAPI = False
    def oddsapi_fetch(sport: str) -> List[Dict]:
        return []

def get_fixtures_multi(sport: str) -> List[Dict[str, Any]]:
    """Router multi-provider: OddsAPI + ESPN + BallDontLie (fallback graceful)."""
    all_fixtures = []
    
    # OddsAPI principal
    if HAS_ODDSAPI:
        try:
            odds_fixtures = oddsapi_fetch(sport)
            all_fixtures.extend(odds_fixtures)
        except Exception:
            pass
    
    # ESPN (cuando esté implementado)
    # try:
    #     from shared.provider_espn import get_scoreboard
    #     espn_data = get_scoreboard(sport)
    #     all_fixtures.extend(espn_data.get('events', []))
    # except:
    #     pass
    
    # BallDontLie NBA (cuando esté)
    # if 'nba' in sport.lower():
    #     try:
    #         from shared.provider_balldontlie import get_games
    #         bdl_games = get_games()
    #         all_fixtures.extend(bdl_games)
    #     except:
    #         pass
    
    return all_fixtures

if __name__ == "__main__":
    print("SCRIPT OK")
