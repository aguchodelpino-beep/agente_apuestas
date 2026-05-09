#!/usr/bin/env bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas

python -m py_compile \
  core/logging.py \
  shared/datetime_utils.py \
  shared/odds.py

pytest tests/core/test_logging.py -v
pytest tests/shared/test_datetime_utils.py -v
pytest tests/shared/test_odds.py -v
pytest tests/test_sharedoddsmath.py -v
pytest tests/ -v

bash scripts/agent_status.sh
bash scripts/runaudit.sh
