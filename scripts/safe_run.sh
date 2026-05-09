#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/aguchodelpino/agente_apuestas"
cd "$ROOT"

[ $# -eq 1 ] || { echo "Uso: bash scripts/safe_run.sh nombre_script.sh"; exit 1; }

script="$1"

case "$script" in
  *.sh) ;;
  *) echo "Solo se permiten scripts .sh"; exit 1 ;;
esac

path="$ROOT/scripts/$script"

[ -f "$path" ] || { echo "No existe: $path"; exit 1; }

bash "$path"
