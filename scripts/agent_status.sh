#!/usr/bin/env bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas || exit 1

count_script_ok_in_scope() {
  local scope="$1"
  local count_ok=0
  local f
  while IFS= read -r f; do
    if timeout 5s sh -c 'PYTHONPATH=. venv/bin/python3 "$1" 2>/dev/null | grep -q "SCRIPT OK"' _ "$f"; then
      count_ok=$((count_ok+1))
    fi
  done < <(find "$scope" -name "*.py" 2>/dev/null | sort)
  echo "$count_ok"
}

echo "=============================================="
echo "AGENTE_APUESTAS 2.0 - ESTADO $(date)"
echo "=============================================="

total_activos=$(find . -name '*.py' \
  -not -path '*/venv/*' \
  -not -path '*/__pycache__/*' \
  -not -path '*/legacy_quarantine/*' | wc -l)

legacy=$(find legacy_quarantine -name '*.py' 2>/dev/null | wc -l || echo 0)

if PYTHONPATH=. venv/bin/python3 -m py_compile departments/**/*.py core/*.py shared/*.py main.py telegrambot.py 2>/dev/null; then
  compilacion="OK"
else
  compilacion="FAIL"
fi

total_ok=0
while IFS= read -r f; do
  if timeout 5s sh -c 'PYTHONPATH=. venv/bin/python3 "$1" 2>/dev/null | grep -q "SCRIPT OK"' _ "$f"; then
    total_ok=$((total_ok+1))
  fi
done < <(find . -name "*.py" \
  -not -path "*/venv/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/legacy_quarantine/*" | sort)

echo
echo "ARQUITECTURA GENERAL:"
echo "  Activos: $total_activos"
echo "  Legacy en cuarentena: $legacy"
echo "  Compilación global: $compilacion"

echo

echo
echo "REGLA DE TRABAJO OBLIGATORIA:"
echo "  1) bash scripts/agent_status.sh"
echo "  2) bash scripts/run_audit.sh"
echo "  3) Luego cualquier parche o desarrollo nuevo"
echo "SCRIPT_OK TOTAL:"
echo "  $total_ok módulos verificados"

echo
echo "DEPARTAMENTOS:"
for dept in core shared departments/deportes/tenis departments/deportes/futbol departments/deportes/basket departments/visuales; do
  total_dept=$(find "$dept" -name "*.py" 2>/dev/null | wc -l)
  ok_dept=$(count_script_ok_in_scope "$dept")
  if [ "$total_dept" -gt 0 ]; then
    echo "  $dept: $ok_dept/$total_dept OK"
  fi
done

echo
echo "LO HECHO:"
echo "  ✅ Core base: config, health"
echo "  ✅ Tenis: handlers/service/repo/models/utils (plantilla maestra)"
echo "  ✅ Visuales: cards/formatter/markdown/telegram_ui"
echo "  ✅ Arranque: main.py, telegrambot.py"
echo "  ✅ Shared: cache, validators"
echo "  ✅ Fútbol/Basket: estructura replicada con SCRIPT_OK"

echo
echo "LO QUE FALTA (prioridad alta):"
echo "  🔄 core/logging.py"
echo "  ✅ shared/datetime_utils.py"
echo "  ✅ shared/odds.py"
echo "  ✅ Tenis -> visuales en telegrambot.py"
echo "  🔄 Datos reales odds API en tenis.repo"

echo
echo "PROXIMO PASO:"
echo "  bash scripts/run_audit.sh"
echo
echo "SCRIPT OK: scripts/agent_status.sh"
