#!/usr/bin/env bash
set -euo pipefail
cd /home/aguchodelpino/agente_apuestas || exit 1
PYTHONPATH=. venv/bin/python3 "$@"
