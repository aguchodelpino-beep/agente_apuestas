#!/bin/bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas

echo "=== PWD ==="
pwd

echo
echo "=== ENV FILES ==="
find . -maxdepth 4 \( -name ".env" -o -name "*.env" -o -name ".env.*" \) -print | sort || true

echo
echo "=== VARIABLES DE API EN .env* ==="
grep -RniE 'ODDS_API|ODDSAPI|THE_ODDS|SOFASCORE|ESPN|PINNACLE|RAPIDAPI|API_KEY|TOKEN' \
  . --include=".env" --include="*.env" --include=".env.*" 2>/dev/null | sed 's/=.*/=***MASKED***/' | head -n 200 || true

echo
echo "=== PROVIDERS / REPOS ==="
find . -maxdepth 4 -type f | grep -Ei 'provider|repo|repository|service|config' | sort | head -n 300 || true

echo
echo "=== REFERENCIAS A ODDS / ESPN / SOFASCORE / PINNACLE ==="
grep -RniE 'provider_theodds_api|get_odds|ODDS_API_KEYS|ODDS_API_KEY|ODDSAPIKEYS|sofascore|espn|pinnacle' \
  . --exclude-dir=venv --exclude-dir=.git --exclude-dir=__pycache__ 2>/dev/null | head -n 300 || true

echo
echo "=== HANDLERS ACTUALES ==="
sed -n '1,220p' handlers.py || true

echo
echo "=== PROVIDER THE ODDS API ==="
sed -n '1,240p' shared/provider_theodds_api.py 2>/dev/null || true

echo
echo "=== CONFIG ==="
sed -n '1,240p' config.py 2>/dev/null || true

echo
echo "=== TENIS/FUTBOL/BASKET FILES ==="
find departments -maxdepth 4 -type f | grep -Ei 'tenis|futbol|basket|formatter|handler|view' | sort || true
