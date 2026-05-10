#!/usr/bin/env bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas || exit 1

mkdir -p data/history cache_enriched tests/shared tests/repos

if [ ! -d venv ]; then
  python3 -m venv venv
fi

. venv/bin/activate
python -m pip install --upgrade pip >/dev/null

if [ -f requirements.txt ]; then
  pip install -r requirements.txt
fi

pip install pytest >/dev/null

echo "SETUP OK"
echo "PYTHON=$(which python)"
echo "PYTEST=$(which pytest)"
