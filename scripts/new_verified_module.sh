#!/usr/bin/env bash
set -uo pipefail

TARGET="${1:-}"
if [ -z "$TARGET" ]; then
  echo "USO: bash scripts/new_verified_module.sh ruta/archivo.py"
  exit 2
fi

created=0

cleanup_on_fail() {
  status=$?
  if [ "$status" -ne 0 ]; then
    echo "SCRIPT FAIL: $TARGET"
    if [ "$created" -eq 1 ] && [ -f "$TARGET" ]; then
      rm -f "$TARGET"
      echo "AUTO-DELETE OK: $TARGET"
    fi
  fi
  exit "$status"
}

trap cleanup_on_fail EXIT

mkdir -p "$(dirname "$TARGET")"

cat > "$TARGET" <<'PY'
from __future__ import annotations

def self_test() -> bool:
    return True

if __name__ == "__main__":
    if not self_test():
        raise SystemExit("SCRIPT FAIL")
    print("SCRIPT OK")
PY

created=1

PYTHONPATH=. venv/bin/python3 -m py_compile "$TARGET"
output="$(PYTHONPATH=. venv/bin/python3 "$TARGET")"
echo "$output"
echo "$output" | grep -q "SCRIPT OK"

trap - EXIT
echo "ARCHIVO VALIDADO Y CONSERVADO: $TARGET"
