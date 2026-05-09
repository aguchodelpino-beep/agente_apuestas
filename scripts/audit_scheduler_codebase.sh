#!/usr/bin/env bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

grep -RniE 'add_job\(|CronTrigger\(' . \
  --include='*.py' \
  --exclude-dir=venv \
  --exclude-dir=.pytest_cache \
  --exclude-dir=__pycache__ \
  --exclude='*.bak*' \
  --exclude='*.pyc' > "$tmp" || true

echo "=============================="
echo "SCHEDULER CODEBASE AUDIT"
echo "=============================="
echo
echo "[1] Referencias encontradas"
cat "$tmp" || true
echo

violations="$(grep -vE '^\./shared/cache_scheduler\.py:|^\./tests/architecture/|^\./tests/scheduler/' "$tmp" || true)"

if [ -n "$violations" ]; then
  echo "[2] VIOLACIONES"
  echo "$violations"
  exit 1
fi

echo "[2] OK: no hay cron jobs fuera del scheduler oficial"
