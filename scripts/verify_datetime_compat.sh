#!/usr/bin/env bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas

python - <<'PY'
from shared.datetime_utils import today_str, now_utc, today_utc
print("today_str =", today_str())
print("now_utc tz =", now_utc().tzinfo)
print("today_utc tz =", today_utc().tzinfo)
PY

pytest tests/repos/test_futbol_repo.py -v
pytest tests/repos/test_tenis_repo.py -v
pytest tests/repos/test_basket_repo.py -v
pytest tests/test_repos.py -v
pytest tests/ -v
