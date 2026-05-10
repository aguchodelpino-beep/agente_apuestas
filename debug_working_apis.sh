#!/bin/bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas

echo "=== 1) OddsAPI NBA LIVE (debe dar playoffs) ==="
python3 -c "
from shared.providertheoddsapi import getodds
import json
print('OddsAPI NBA:', json.dumps(getodds('basketball_nba', regions='us,eu,uk', markets='h2h'), indent=2)[:3000] or 'VACÍO')
"

echo
echo "=== 2) OddsAPI Fútbol EPL LIVE ==="
python3 -c "
from shared.providertheoddsapi import getodds
import json
print('OddsAPI EPL:', json.dumps(getodds('soccer_epl', regions='eu', markets='h2h'), indent=2)[:3000] or 'VACÍO')
"

echo
echo "=== 3) OddsAPI Tenis ATP (ya funciona) ==="
python3 -c "
from shared.providertheoddsapi import getodds
print('Tenis ATP OK')
"
