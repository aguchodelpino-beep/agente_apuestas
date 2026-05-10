#!/usr/bin/env bash
set -euo pipefail

TS="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="backups_autofix/snapshot_tenis_green_${TS}"

mkdir -p "$BACKUP_DIR"
cp -r departments/deportes/tenis/ "$BACKUP_DIR/"
cp scripts/fix_tenis_picks_text_safe.sh "$BACKUP_DIR/"

echo "Snapshot estable guardado en $BACKUP_DIR"

echo "Actualizando auditoría..."
bash scripts/agent_status.sh
bash scripts/run_audit.sh

echo "Verificando estado post-snapshot..."
pytest tests/services/test_tenis_formatter_integration.py -v
pytest tests/ -v

echo "OK: snapshot tenis green creado y validado"
