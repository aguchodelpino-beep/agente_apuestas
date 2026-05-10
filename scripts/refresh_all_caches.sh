#!/usr/bin/env bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas
mkdir -p logs
TS="$(date +%Y%m%d_%H%M%S)"
LOG_FILE="logs/refresh_all_caches_${TS}.log"

exec > >(tee -a "$LOG_FILE") 2>&1

echo "=================================================="
echo "REFRESH ALL CACHES START $(date)"
echo "LOG_FILE=$LOG_FILE"
echo "=================================================="

export PYTHONPATH=.

run_step() {
  local label="$1"
  shift
  echo
  echo "[STEP] $label"
  if "$@"; then
    echo "[OK] $label"
  else
    echo "[ERROR] $label"
    return 1
  fi
}

warn_step() {
  local label="$1"
  shift
  echo
  echo "[STEP-OPTIONAL] $label"
  if "$@"; then
    echo "[OK] $label"
  else
    echo "[WARN] $label"
  fi
}

run_step "refresh_oddsapi_priority" python3 scripts/refresh_oddsapi_priority.py

warn_step "refresh_priority_leagues" python3 scripts/refresh_priority_leagues.py
warn_step "refresh_espn_cache" python3 scripts/refresh_espn_cache.py
warn_step "refresh_pinnacle_cache" python3 scripts/refresh_pinnacle_cache.py

TODAY="$(date +%Y-%m-%d)"

if [ -f "data/raw/futbol/${TODAY}.json" ]; then
  cp "data/raw/futbol/${TODAY}.json" "departments/deportes/futbol/live_today.json"
  echo "[OK] copied futbol cache"
else
  echo "[WARN] missing data/raw/futbol/${TODAY}.json"
fi

if [ -f "data/raw/basket/${TODAY}.json" ]; then
  cp "data/raw/basket/${TODAY}.json" "departments/deportes/basket/live_today.json"
  echo "[OK] copied basket cache"
else
  echo "[WARN] missing data/raw/basket/${TODAY}.json"
fi

warn_step "refresh futbol repo cache" python3 - <<'PY'
from departments.deportes.futbol.repo import refresh_cache
refresh_cache()
print("futbol refresh_cache ok")
PY

warn_step "refresh basket repo cache" python3 - <<'PY'
from departments.deportes.basket.repo import refresh_cache
refresh_cache()
print("basket refresh_cache ok")
PY

echo
echo "[CHECK] unique leagues in live_today.json"
python3 - <<'PY'
import json
from pathlib import Path

paths = {
    "futbol": Path("departments/deportes/futbol/live_today.json"),
    "basket": Path("departments/deportes/basket/live_today.json"),
}
for sport, path in paths.items():
    if not path.exists():
        print(f"{sport}: missing file")
        continue
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"{sport}: invalid json -> {e}")
        continue
    leagues = sorted({str(x.get('league','')).strip() for x in data if isinstance(x, dict) and str(x.get('league','')).strip()})
    print(f"{sport}: rows={len(data)} unique_leagues={len(leagues)} sample={leagues[:10]}")
PY

run_step "pytest full suite" pytest tests/ -v

echo
echo "=================================================="
echo "REFRESH ALL CACHES DONE $(date)"
echo "LOG_FILE=$LOG_FILE"
echo "=================================================="
