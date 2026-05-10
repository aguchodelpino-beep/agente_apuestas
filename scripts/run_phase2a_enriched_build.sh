#!/usr/bin/env bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas || exit 1

if [ ! -f venv/bin/activate ]; then
  echo "❌ No existe venv/bin/activate"
  exit 1
fi

. venv/bin/activate

echo "=== VENV ==="
echo "VIRTUAL_ENV=${VIRTUAL_ENV:-}"
which python
which pip
python -c "import sys; print('IN_VENV=', sys.prefix != sys.base_prefix)"

mkdir -p cache_enriched

echo "=== PYTEST TARGET ==="
pytest -q tests/scripts/test_build_enriched_cache.py tests/shared/test_enriched_cache_builder.py

for sport in futbol basket tenis; do
  echo "=== BUILD ENRICHED: ${sport} ==="
  PYTHONPATH=. python3 -m scripts.build_enriched_cache "${sport}" || true
done

echo "=== CACHE ENRICHED FILES ==="
find cache_enriched -maxdepth 1 -type f | sort

echo "=== PREVIEW ENRICHED FILES ==="
for f in cache_enriched/*.json; do
  [ -f "$f" ] || continue
  echo "===== ${f} ====="
  head -n 40 "$f"
done

echo "SCRIPT OK: run_phase2a_enriched_build"
