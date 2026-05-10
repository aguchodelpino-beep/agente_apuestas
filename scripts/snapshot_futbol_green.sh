#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/aguchodelpino/agente_apuestas"
OUTSIDE_BASE="/home/aguchodelpino/agente_apuestas_backups"
TS="$(date +%Y%m%d_%H%M%S)"
SNAP_DIR="$OUTSIDE_BASE/snapshot_futbol_green_${TS}"

cd "$PROJECT_DIR"
mkdir -p "$SNAP_DIR"

echo "[1/6] Guardando snapshot fuera del repo..."
mkdir -p "$SNAP_DIR"
cp -r departments/deportes/futbol "$SNAP_DIR/"
cp scripts/bootstrap_futbol_basket_handlers_safe.sh "$SNAP_DIR/" 2>/dev/null || true

echo "[2/6] Validando arquitectura..."
bash scripts/run_audit.sh

echo "[3/6] Validando tests completos..."
pytest tests/ -v

echo "[4/6] Validando unittest..."
python -m unittest discover -s tests -v

echo "[5/6] Mostrando estado..."
bash scripts/agent_status.sh

echo "[6/6] OK snapshot futbol guardado en $SNAP_DIR"
