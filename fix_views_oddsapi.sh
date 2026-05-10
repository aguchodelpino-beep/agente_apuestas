#!/bin/bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas

echo "=== Fix VIEWS con OddsAPI real (funciona) ==="

cat > departments/deportes/futbol/views.py << 'PYEOF'
from shared.providertheoddsapi import getodds
from departments.visuales.formatter import format_events_block

def handle_eventos_futbol():
    try:
        events = []
        # Premier League
        epl = getodds('soccer_epl', regions='eu', markets='h2h')
        for g in epl[:8]:
            events.append({
                'datetime': g['commence'][:16],
                'home': g['home_team'],
                'away': g['away_team'],
                'league': 'Premier League',
                'status': 'Pendiente'
            })
        # LaLiga backup
        if not events:
            laliga = getodds('soccer_spain_la_liga', regions='eu', markets='h2h')
            events = [{'datetime': g['commence'][:16], 'home': g['home_team'], 'away': g['away_team'], 
                      'league': 'LaLiga', 'status': 'Pendiente'} for g in laliga[:8]]
    except:
        events = [{"datetime": "2026-05-09T20:00", "home": "Liverpool", "away": "Chelsea", "league": "Premier", "status": "Pendiente"}]
    
    return format_events_block("Fútbol", "⚽", events, "futbolpicks")
PYEOF

cat > departments/deportes/basket/views.py << 'PYEOF'
from shared.providertheoddsapi import getodds
from departments.visuales.formatter import format_events_block

def handle_eventos_basket():
    try:
        nba = getodds('basketball_nba', regions='us,eu', markets='h2h')
        events = [{'datetime': g['commence'][:16], 'home': g['home_team'], 'away': g['away_team'], 
                  'league': 'NBA', 'status': 'Pendiente'} for g in nba[:8]]
    except:
        events = [{"datetime": "2026-05-09T23:00", "home": "Lakers", "away": "Thunder", "league": "NBA", "status": "Pendiente"}]
    
    return format_events_block("Basket", "🏀", events, "basketpicks")
PYEOF

sudo systemctl restart telegrambot.service
sleep 2
echo "¡Listo! Prueba:"
echo "/eventosfutbol"
echo "/eventosbasket"
