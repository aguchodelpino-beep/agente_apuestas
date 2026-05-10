#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/aguchodelpino/agente_apuestas"
cd "$PROJECT_DIR"

echo "[1/8] Estado general..."
bash scripts/agent_status.sh

echo "[2/8] Auditoría global..."
bash scripts/run_audit.sh

echo "[3/8] Archivos basket..."
ls -la departments/deportes/basket

echo "[4/8] Compilación basket real..."
python3 -m py_compile \
  departments/deportes/basket/handlers.py \
  departments/deportes/basket/service.py \
  departments/deportes/basket/repo.py \
  departments/deportes/basket/models.py \
  departments/deportes/basket/views.py \
  departments/deportes/basket/urls.py \
  departments/deportes/basket/balldontlie_handlers.py \
  departments/deportes/basket/balldontlie_service.py

echo "[5/8] Smoke import basket..."
python3 - <<'PY'
from departments.deportes.basket.handlers import handle_eventos_basket, handle_basket_picks
print("IMPORT_OK", callable(handle_eventos_basket), callable(handle_basket_picks))
print(handle_eventos_basket())
print(handle_basket_picks())
PY

echo "[6/8] Tests basket..."
pytest tests/providers/test_basket_provider.py -v
pytest tests/repos/test_basket_repo.py -v
pytest tests/services/test_basket_service.py -v

echo "[7/8] Tests globales..."
pytest tests/ -v
python -m unittest discover -s tests -v

echo "[8/8] OK basket audit listo"
