#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${1:-/home/aguchodelpino/agente_apuestas}"
cd "$PROJECT_DIR"

SERVICE="departments/deportes/tenis/service.py"
VIEWS="departments/deportes/tenis/views.py"
HANDLERS="departments/deportes/tenis/handlers.py"
TEST_ONE="tests/services/test_tenis_formatter_integration.py"

for f in "$SERVICE" "$VIEWS" "$HANDLERS"; do
  [ -f "$f" ] || { echo "ERROR: falta $f"; exit 1; }
done

TS="$(date +%Y%m%d_%H%M%S)"
TMPDIR="$(mktemp -d)"
cleanup(){ rm -rf "$TMPDIR"; }
trap cleanup EXIT

cp "$SERVICE"  "$TMPDIR/service.py.bak"
cp "$VIEWS"    "$TMPDIR/views.py.bak"
cp "$HANDLERS" "$TMPDIR/handlers.py.bak"

rollback() {
  echo
  echo "[ROLLBACK] Restaurando archivos originales..."
  cp "$TMPDIR/service.py.bak"  "$SERVICE"
  cp "$TMPDIR/views.py.bak"    "$VIEWS"
  cp "$TMPDIR/handlers.py.bak" "$HANDLERS"
}

echo "[1/6] Detectando funciones existentes en service.py..."
python3 - <<'PY' > "$TMPDIR/service_funcs.txt"
import ast, pathlib
p = pathlib.Path("departments/deportes/tenis/service.py")
mod = ast.parse(p.read_text(encoding="utf-8"))
funcs = [n.name for n in mod.body if isinstance(n, ast.FunctionDef)]
for x in funcs:
    print(x)
PY

echo "[2/6] Preparando parche mínimo compatible..."
python3 - <<'PY'
from pathlib import Path

service = Path("departments/deportes/tenis/service.py")
funcs = set(Path(".").joinpath("").read_text() if False else [])
detected = set(Path("/tmp/does_not_matter").read_text() for _ in [] ) if False else set()
detected = set(Path("$(pwd)").read_text() for _ in [] ) if False else detected
PY

python3 - <<'PY'
from pathlib import Path

service = Path("departments/deportes/tenis/service.py")
detected = set(Path(".").read_text() for _ in []) if False else set(Path("scripts").read_text() for _ in []) if False else None
PY

python3 - <<'PY'
from pathlib import Path

service = Path("departments/deportes/tenis/service.py")
funcs = set(Path("/dev/null").read_text() for _ in []) if False else set()
with open("/tmp/fix_tenis_funcs_runtime.txt", "w", encoding="utf-8") as f:
    pass
PY

cp "$TMPDIR/service_funcs.txt" /tmp/fix_tenis_funcs_runtime.txt

python3 - <<'PY'
from pathlib import Path

service = Path("departments/deportes/tenis/service.py")
funcs = {line.strip() for line in Path("/tmp/fix_tenis_funcs_runtime.txt").read_text(encoding="utf-8").splitlines() if line.strip()}

targets = {
    "get_fixtures": ["list_fixtures", "get_fixtures"],
    "get_live": ["list_live_fixtures", "get_live", "get_live_fixtures"],
    "get_one": ["get_fixture_by_id", "get_one", "get_by_id"],
}

append = []

def pick(candidates):
    for c in candidates:
        if c in funcs:
            return c
    return None

mapping = {k: pick(v) for k, v in targets.items()}

text = service.read_text(encoding="utf-8")

if "def get_fixtures(" not in text:
    src = mapping["get_fixtures"]
    if src and src != "get_fixtures":
        append.append(f"""
def get_fixtures(*args, **kwargs):
    return {src}(*args, **kwargs)
""".rstrip())

if "def get_live(" not in text:
    src = mapping["get_live"]
    if src and src != "get_live":
        append.append(f"""
def get_live(*args, **kwargs):
    return {src}(*args, **kwargs)
""".rstrip())

if "def get_one(" not in text:
    src = mapping["get_one"]
    if src and src != "get_one":
        append.append(f"""
def get_one(*args, **kwargs):
    return {src}(*args, **kwargs)
""".rstrip())

if not append:
    print("NO_PATCH_NEEDED")
else:
    service.write_text(text.rstrip() + "\n\n" + "\n\n".join(append) + "\n", encoding="utf-8")
    print("PATCH_APPLIED")
    for block in append:
        head = block.splitlines()[0].strip()
        print(head)
PY

echo "[3/6] Verificando sintaxis..."
if ! python3 -m py_compile "$SERVICE" "$VIEWS" "$HANDLERS"; then
  rollback
  echo "ERROR: py_compile falló"
  exit 1
fi

echo "[4/6] Ejecutando pytest focalizado..."
if ! pytest "$TEST_ONE" -v; then
  rollback
  echo "ERROR: falló $TEST_ONE"
  exit 1
fi

echo "[5/6] Ejecutando suite pytest completa..."
if ! pytest tests/ -v; then
  rollback
  echo "ERROR: falló pytest tests/ -v"
  exit 1
fi

echo "[6/6] Ejecutando unittest discover..."
if ! python -m unittest discover -s tests -v; then
  rollback
  echo "ERROR: falló unittest discover"
  exit 1
fi

mkdir -p backups_autofix
cp "$TMPDIR/service.py.bak"  "backups_autofix/tenis_service_${TS}.bak"
cp "$TMPDIR/views.py.bak"    "backups_autofix/tenis_views_${TS}.bak"
cp "$TMPDIR/handlers.py.bak" "backups_autofix/tenis_handlers_${TS}.bak"

echo
echo "OK: parche aplicado y validado"
echo "Backups guardados en backups_autofix/"
