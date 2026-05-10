#!/bin/bash
set -euo pipefail

cat >> handlers.py << 'PYEOF'


def fetch_oddsapi_events(sport_key: str = "tennis_atp"):
    """Conecta OddsAPI para eventos reales"""
    import requests
    import os
    import json
    from datetime import datetime, timedelta
    
    api_key = os.getenv("ODDSAPI_KEY") or "tu_key_aqui"
    endpoint = "https://api.the-odds-api.com/v4/sports"
    
    try:
        params = {
            "apiKey": api_key,
            "regions": "eu",
            "markets": "h2h",
            "oddsFormat": "decimal"
        }
        
        r = requests.get(f"{endpoint}/{sport_key}/odds", params=params, timeout=10)
        
        if r.status_code == 200:
            odds_json = r.json()
            events = []
            
            for game in odds_json:
                commence = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00'))
                if datetime.now() <= commence <= datetime.now() + timedelta(hours=24):
                    home_odds = None
                    away_odds = None
                    
                    for book in game.get('bookmakers', []):
                        for market in book.get('markets', []):
                            if market['key'] == 'h2h':
                                outcomes = market['outcomes']
                                if len(outcomes) >= 2:
                                    home_odds = outcomes[0]['price']
                                    away_odds = outcomes[1]['price']
                                    break
                    
                    events.append({
                        "datetime": commence.strftime("%Y-%m-%dT%H:%M"),
                        "home": game['home_team'],
                        "away": game['away_team'], 
                        "league": game['sport_key'].replace('_', ' ').title(),
                        "status": "Pendiente",
                        "odds_home": home_odds,
                        "odds_away": away_odds
                    })
            return events
        else:
            print(f"OddsAPI error: {r.status_code}")
            return []
    except Exception as e:
        print(f"Error OddsAPI: {e}")
        return []


def handle_eventos_tenis_real() -> str:
    events = fetch_oddsapi_events("tennis_atp") + fetch_oddsapi_events("tennis_wta")
    return format_events_block("Tenis", "🎾", events, "tenispicks")


def handle_eventos_futbol_real() -> str:
    events = fetch_oddsapi_events("soccer_epl") + fetch_oddsapi_events("soccer_la_liga")
    return format_events_block("Fútbol", "⚽", events, "futbolpicks")
PYEOF

sudo systemctl restart telegrambot.service
echo "Listo. Configura ODDSAPI_KEY en .env y reinicia"
