#!/usr/bin/env bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas

echo "=============================="
echo "CHECK TENIS REAL ODDS"
echo "=============================="

grep -RniE 'odds|quota|cuota|bookmaker|market|mercado|sportsgameodds|odds_api|theodds|rapidapi|espn|cache' \
  departments/deportes/tenis/repo.py \
  departments/deportes/tenis/service.py \
  shared \
  2>/dev/null || true

echo
echo "[repo.py funciones]"
grep -nE '^def |^class ' departments/deportes/tenis/repo.py 2>/dev/null || true

echo
echo "[service.py funciones]"
grep -nE '^def |^class ' departments/deportes/tenis/service.py 2>/dev/null || true

echo
echo "CHECK TENIS REAL ODDS OK"
