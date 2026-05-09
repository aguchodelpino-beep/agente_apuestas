#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/aguchodelpino/agente_apuestas"
cd "$ROOT"

usage() {
  echo "USO:"
  echo "  bash scripts/new_component_verified.sh deporte futbol handlers"
  echo "  bash scripts/new_component_verified.sh deporte tenis service"
  echo "  bash scripts/new_component_verified.sh deporte basket repo"
  echo "  bash scripts/new_component_verified.sh deporte futbol models"
  echo "  bash scripts/new_component_verified.sh visuales formatter"
  echo "  bash scripts/new_component_verified.sh visuales telegram_ui"
  exit 2
}

[ "$#" -ge 2 ] || usage

scope="${1:-}"
name="${2:-}"
kind="${3:-}"

target=""

case "$scope" in
  deporte)
    [ -n "$kind" ] || usage
    case "$name" in
      futbol|tenis|basket) ;;
      *) echo "DEPORTE INVALIDO: $name"; exit 3 ;;
    esac
    case "$kind" in
      handlers|service|repo|models) ;;
      *) echo "TIPO INVALIDO: $kind"; exit 4 ;;
    esac
    target="departments/deportes/$name/$kind.py"
    ;;
  visuales)
    case "$name" in
      formatter|markdown|cards|telegram_ui) ;;
      *) echo "MODULO VISUAL INVALIDO: $name"; exit 5 ;;
    esac
    target="departments/visuales/$name.py"
    ;;
  *)
    usage
    ;;
esac

mkdir -p "$(dirname "$target")"

if [ -e "$target" ]; then
  echo "YA EXISTE: $target"
  exit 0
fi

bash scripts/new_verified_module.sh "$target"

PYTHONPATH=. venv/bin/python3 -m py_compile "$target"
PYTHONPATH=. venv/bin/python3 "$target" | grep -q "SCRIPT OK"

echo "COMPONENTE OK: $target"
