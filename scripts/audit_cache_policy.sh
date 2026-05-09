#!/usr/bin/env bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas

echo "=============================="
echo "CACHE POLICY AUDIT"
echo "=============================="

echo
echo "[1] REPOS cache-only"
grep -RniE 'load_sport_day|requests\.|httpx\.|urllib\.|provider_|espn_get|get_odds\(' \
  departments/deportes/futbol/repo.py \
  departments/deportes/basket/repo.py \
  departments/deportes/tenis/repo.py \
  2>/dev/null || true

echo
echo "[2] Scheduler oficial"
grep -nE 'TZ = |CronTrigger|daily_cache_2am_ec|ensure_today_cache_once|build_all_caches' \
  shared/cache_scheduler.py 2>/dev/null || true

echo
echo "[3] Legacy scheduler"
grep -nE 'refresh_tenis|refresh_futbol|refresh_basket|register_example_jobs|add_job' \
  scheduler.py 2>/dev/null || true

echo
echo "CACHE POLICY AUDIT OK"
