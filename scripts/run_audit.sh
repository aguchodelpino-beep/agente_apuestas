#!/usr/bin/env bash
set -euo pipefail
cd /home/aguchodelpino/agente_apuestas || exit 1
python3 scripts/audit_architecture.py
