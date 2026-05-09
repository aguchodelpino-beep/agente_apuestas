#!/usr/bin/env bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas

echo "== STATUS =="
bash scripts/agent_status.sh

echo
echo "== AUDIT =="
bash scripts/runaudit.sh

echo
echo "== SNAPSHOT TESTS =="
pytest tests/test_architecture_doc.py -v
pytest tests/test_provider_utils.py -v
pytest tests/ -v
