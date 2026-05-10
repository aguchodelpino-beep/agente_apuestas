#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/aguchodelpino/agente_apuestas"
cd "$PROJECT_DIR"

echo "[1/7] Estado general..."
bash scripts/agent_status.sh

echo "[2/7] Auditoría global..."
bash scripts/run_audit.sh

echo "[3/7] Archivos basket..."
ls -la departments/deportes/basket

echo "[4/7] Compilación basket..."
python3 -m py_compile \
  departments/deportes/basket/handlers.py \
  departments/deportes/basket/service.py \
  departments/deportes/basket/repo.py \
  departments/deportes/basket/models.py \
  departments/deportes/basket/provider.py

echo "[5/7] Smoke import basket..."
python3 - <<'PY'
from departments.deportes.basket.handlers import handle_eventos_basket, handle_basket_picks
print("IMPORT_OK", callable(handle_eventos_basket), callable(handle_basket_picks))
print(handle_eventos_basket())
print(handle_basket_picks())
PY

echo "[6/7] Tests basket..."
pytest tests/providers/test_basket_provider.py -v
pytest tests/repos/test_basket_repo.py -v
pytest tests/services/test_basket_service.py -v

echo "[7/7] OK basket audit listo"
