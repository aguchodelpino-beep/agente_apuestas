#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/aguchodelpino/agente_apuestas"
OUTSIDE_BASE="/home/aguchodelpino/agente_apuestas_backups"
TS="$(date +%Y%m%d_%H%M%S)"
SNAP_DIR="$OUTSIDE_BASE/snapshot_futbol_basket_${TS}"

cd "$PROJECT_DIR"

echo "[1/8] Creando snapshot fuera del repo..."
mkdir -p "$SNAP_DIR"
cp -r departments/deportes/futbol "$SNAP_DIR/"
cp -r departments/deportes/basket "$SNAP_DIR/"
cp scripts/bootstrap_futbol_basket_handlers_safe.sh "$SNAP_DIR/" 2>/dev/null || true

echo "[2/8] Estado actual..."
bash scripts/agent_status.sh

echo "[3/8] Auditoría global..."
bash scripts/run_audit.sh

echo "[4/8] Compilación focal..."
python3 -m py_compile \
  departments/deportes/futbol/handlers.py \
  departments/deportes/basket/handlers.py \
  departments/deportes/futbol/service.py \
  departments/deportes/basket/service.py

echo "[5/8] Smoke imports..."
python3 - <<'PY'
from departments.deportes.futbol.handlers import handle_eventos_futbol, handle_futbol_picks
from departments.deportes.basket.handlers import handle_eventos_basket, handle_basket_picks
print("FUTBOL_OK", callable(handle_eventos_futbol), callable(handle_futbol_picks))
print("BASKET_OK", callable(handle_eventos_basket), callable(handle_basket_picks))
PY

echo "[6/8] Tests completos..."
pytest tests/ -v

echo "[7/8] Unittest..."
python -m unittest discover -s tests -v

echo "[8/8] OK snapshot y auditoría listos en $SNAP_DIR"
