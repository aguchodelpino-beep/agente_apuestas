#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/aguchodelpino/agente_apuestas"

usage() {
  echo "Uso:"
  echo "  bash scripts/new_component.sh deporte futbol handlers"
  echo "  bash scripts/new_component.sh deporte tenis service"
  echo "  bash scripts/new_component.sh deporte basket repo"
  echo "  bash scripts/new_component.sh deporte futbol models"
  echo "  bash scripts/new_component.sh visuales formatter"
  exit 1
}

[ $# -ge 2 ] || usage

scope="$1"
name="$2"
kind="${3:-}"

case "$scope" in
  deporte)
    [ -n "$kind" ] || usage
    case "$name" in
      futbol|tenis|basket) ;;
      *) echo "Deporte invalido: $name"; exit 1 ;;
    esac
    case "$kind" in
      handlers|service|repo|models) ;;
      *) echo "Tipo invalido: $kind"; exit 1 ;;
    esac
    target="$ROOT/departments/deportes/$name/$kind.py"
    ;;
  visuales)
    case "$name" in
      formatter|markdown|cards|telegram_ui) ;;
      *) echo "Modulo visual invalido: $name"; exit 1 ;;
    esac
    target="$ROOT/departments/visuales/$name.py"
    ;;
  *)
    usage
    ;;
esac

mkdir -p "$(dirname "$target")"

if [ -e "$target" ]; then
  echo "Ya existe: $target"
  exit 0
fi

cat > "$target" <<PY
\"\"\"$target\"\"\"
PY

echo "Creado: $target"
