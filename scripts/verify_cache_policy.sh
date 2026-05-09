#!/usr/bin/env bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas

python -m py_compile \
  shared/cache_scheduler.py \
  scheduler.py \
  departments/deportes/futbol/repo.py \
  departments/deportes/basket/repo.py \
  departments/deportes/tenis/repo.py

pytest tests/architecture/test_cache_only_repos.py -v
pytest tests/architecture/test_scheduler_policy.py -v
pytest tests/repos/test_futbol_repo.py -v
pytest tests/repos/test_basket_repo.py -v
pytest tests/repos/test_tenis_repo.py -v
pytest tests/ -v

bash scripts/audit_cache_policy.sh
