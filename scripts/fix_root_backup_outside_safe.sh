#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/aguchodelpino/agente_apuestas"
OUTSIDE_BASE="/home/aguchodelpino/agente_apuestas_backups"
SRC="$PROJECT_DIR/backups_autofix"
TS="$(date +%Y%m%d_%H%M%S)"
DST="$OUTSIDE_BASE/backups_autofix_${TS}"

cd "$PROJECT_DIR"

rollback() {
  echo
  echo "[ROLLBACK] Restaurando backups_autofix dentro del repo..."
  if [ -d "$DST" ] && [ ! -d "$SRC" ]; then
    mv "$DST" "$SRC"
  fi
}

if [ ! -d "$SRC" ]; then
  echo "No existe $SRC; nada que mover."
  echo "Validando arquitectura..."
  bash scripts/run_audit.sh
  exit 0
fi

mkdir -p "$OUTSIDE_BASE"

echo "[1/5] Moviendo backups fuera del repo..."
mv "$SRC" "$DST"

echo "[2/5] Validando que el root quedó limpio..."
if [ -d "$SRC" ]; then
  rollback
  echo "ERROR: backups_autofix sigue dentro del repo"
  exit 1
fi

echo "[3/5] Ejecutando auditoría..."
if ! bash scripts/run_audit.sh; then
  rollback
  echo "ERROR: run_audit.sh falló"
  exit 1
fi

echo "[4/5] Ejecutando pytest suite completa..."
if ! pytest tests/ -v; then
  rollback
  echo "ERROR: pytest tests/ -v falló"
  exit 1
fi

echo "[5/5] Ejecutando unittest discover..."
if ! python -m unittest discover -s tests -v; then
  rollback
  echo "ERROR: unittest discover falló"
  exit 1
fi

echo
echo "OK: backups movidos fuera del repo a $DST"
echo "ARQUITECTURA limpia y tests OK"
