#!/usr/bin/env bash
set -euo pipefail
cd /home/aguchodelpino/agente_apuestas

echo
echo "================ STATUS ================"
bash scripts/agent_status.sh || true

echo
echo "================ AUDIT GENERAL ================"
bash scripts/run_audit.sh || true

echo
echo "================ TENIS CHAIN ================"
bash scripts/audit_tenis_chain.sh || true

echo
echo "================ TENIS REAL ODDS ================"
bash scripts/check_tenis_real_odds.sh || true

echo
echo "================ PLACEHOLDERS ================"
grep -RniE 'todo|tbd|lorem ipsum' ARCHITECTURE.md departments shared telegrambot.py 2>/dev/null || true

echo
echo "================ PYTEST ================"
pytest tests/ -v
