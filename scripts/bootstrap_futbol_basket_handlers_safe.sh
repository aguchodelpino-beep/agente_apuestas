#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/aguchodelpino/agente_apuestas"
cd "$PROJECT_DIR"

FUTBOL="departments/deportes/futbol/handlers.py"
BASKET="departments/deportes/basket/handlers.py"
TS="$(date +%Y%m%d_%H%M%S)"
TMPDIR="$(mktemp -d)"
cleanup(){ rm -rf "$TMPDIR"; }
trap cleanup EXIT

for f in "$FUTBOL" "$BASKET"; do
  [ -f "$f" ] || { echo "ERROR: falta $f"; exit 1; }
done

cp "$FUTBOL" "$TMPDIR/futbol.handlers.py.bak"
cp "$BASKET" "$TMPDIR/basket.handlers.py.bak"

rollback() {
  echo
  echo "[ROLLBACK] Restaurando handlers originales..."
  cp "$TMPDIR/futbol.handlers.py.bak" "$FUTBOL"
  cp "$TMPDIR/basket.handlers.py.bak" "$BASKET"
}

echo "[1/7] Reescribiendo handlers.py de futbol..."
cat > "$FUTBOL" <<'PYEOF'
from __future__ import annotations

def build_event_cards(limit: int = 10) -> list[dict]:
    return []

def handle_eventos_futbol(*args, **kwargs) -> str:
    return "⚽ EVENTOS FUTBOL\n\nSin eventos disponibles."

def handle_futbol_picks(*args, **kwargs) -> str:
    return "⚽ FUTBOL PICKS\n\nSin picks disponibles en la capa analítica."

__all__ = ["build_event_cards", "handle_eventos_futbol", "handle_futbol_picks"]
PYEOF

echo "[2/7] Reescribiendo handlers.py de basket..."
cat > "$BASKET" <<'PYEOF'
from __future__ import annotations

def build_event_cards(limit: int = 10) -> list[dict]:
    return []

def handle_eventos_basket(*args, **kwargs) -> str:
    return "🏀 EVENTOS BASKET\n\nSin eventos disponibles."

def handle_basket_picks(*args, **kwargs) -> str:
    return "🏀 BASKET PICKS\n\nSin picks disponibles en la capa analítica."

__all__ = ["build_event_cards", "handle_eventos_basket", "handle_basket_picks"]
PYEOF

echo "[3/7] Verificando archivos..."
sed -n '1,120p' "$FUTBOL"
sed -n '1,120p' "$BASKET"

echo "[4/7] Compilando..."
if ! python3 -m py_compile "$FUTBOL" "$BASKET"; then
  rollback
  echo "ERROR: py_compile falló"
  exit 1
fi

echo "[5/7] Smoke import..."
if ! python3 - <<'PY'
from departments.deportes.futbol.handlers import handle_eventos_futbol, handle_futbol_picks
from departments.deportes.basket.handlers import handle_eventos_basket, handle_basket_picks
print("IMPORT_OK",
      callable(handle_eventos_futbol),
      callable(handle_futbol_picks),
      callable(handle_eventos_basket),
      callable(handle_basket_picks))
PY
then
  rollback
  echo "ERROR: smoke import falló"
  exit 1
fi

echo "[6/7] Ejecutando pytest suite completa..."
if ! pytest tests/ -v; then
  rollback
  echo "ERROR: pytest tests/ -v falló"
  exit 1
fi

echo "[7/7] Ejecutando auditoría..."
if ! bash scripts/run_audit.sh; then
  rollback
  echo "ERROR: run_audit.sh falló"
  exit 1
fi

echo
echo "OK: bootstrap mínimo de futbol y basket aplicado y validado"
