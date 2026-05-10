#!/bin/bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas

echo "=== 1) DEBUG ESPN NBA (debe dar playoffs) ==="
python3 -c "
from shared.providerespn import espn_get_basketball_nba_scoreboard
import json
today = '2026-05-09'
print('ESPN NBA:', json.dumps(espn_get_basketball_nba_scoreboard({'dates': today}), indent=2)[:2000])
"

echo
echo "=== 2) DEBUG ESPN Fútbol Premier (Liverpool vs Chelsea) ==="
python3 -c "
from shared.providerespn import espn_get_f_soccer_league_scoreboard
import json
print('ESPN Premier:', json.dumps(espn_get_f_soccer_league_scoreboard('eng.1', {'dates': '2026-05-09'}), indent=2)[:2000])
"

echo
echo "=== 3) DEBUG OddsAPI NBA ==="
python3 -c "
from shared.providertheoddsapi import getodds
import json
print('OddsAPI NBA:', json.dumps(getodds('basketball_nba', regions='us,eu', markets='h2h'), indent=2)[:2000])
"

echo
echo "=== 4) BallDontLie NBA ==="
python3 -c "
from shared.providerballdontlie import balldontlie_games
import json
print('BallDontLie:', json.dumps(balldontlie_games(days_ahead=2), indent=2)[:2000])
"
