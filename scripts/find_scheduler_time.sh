#!/usr/bin/env bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas

grep -RniE '02:00|2:00|hour.?=.2|cron|BackgroundScheduler|America/Guayaquil|daily_cache_2am_ec|build_all_caches|ensure_today_cache_once' \
  shared scheduler.py main.py scripts 2>/dev/null || true
