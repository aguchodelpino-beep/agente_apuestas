#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/aguchodelpino/agente_apuestas"
cd "$PROJECT_DIR"

FUTBOL="departments/deportes/futbol/handlers.py"
BASKET="departments/deportes/basket/handlers.py"
TMPDIR="$(mktemp -d)"

cleanup() {
  rm -rf "$TMPDIR"
}
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

echo "[1/8] Reescribiendo handlers de futbol..."
cat > "$FUTBOL" <<'PYEOF'
from __future__ import annotations

try:
    from departments.deportes.futbol.views import handle_eventos_futbol as _view_handle_eventos_futbol
except Exception:
    _view_handle_eventos_futbol = None

def build_event_cards(limit: int = 10) -> list[dict]:
    if _view_handle_eventos_futbol is None:
        return []
    try:
        data = _view_handle_eventos_futbol()
        if isinstance(data, list):
            return data[:limit]
    except Exception:
        pass
    return []

def handle_eventos_futbol(*args, **kwargs) -> str:
    cards = build_event_cards()
    if not cards:
        if _view_handle_eventos_futbol is not None:
            try:
                out = _view_handle_eventos_futbol(*args, **kwargs)
                if isinstance(out, str):
                    return out
            except Exception:
                pass
        return "EVENTOS FUTBOL\n\nSin eventos disponibles."
    lines = ["EVENTOS FUTBOL", ""]
    for item in cards:
        title = item.get("title", "Partido")
        league = item.get("league", "Liga")
        start = item.get("start", "N/D")
        markets = item.get("markets", 0)
        lines.append(f"- {title} | {league} | {start} | mercados: {markets}")
    return "\n".join(lines)

def handle_futbol_picks(*args, **kwargs) -> str:
    return "FUTBOL PICKS\n\nSin picks disponibles en la capa analitica."

__all__ = ["build_event_cards", "handle_eventos_futbol", "handle_futbol_picks"]
PYEOF

echo "[2/8] Reescribiendo handlers de basket..."
cat > "$BASKET" <<'PYEOF'
from __future__ import annotations

try:
    from departments.deportes.basket.views import handle_eventos_basket as _view_handle_eventos_basket
except Exception:
    _view_handle_eventos_basket = None

def build_event_cards(limit: int = 10) -> list[dict]:
    if _view_handle_eventos_basket is None:
        return []
    try:
        data = _view_handle_eventos_basket()
        if isinstance(data, list):
            return data[:limit]
    except Exception:
        pass
    return []

def handle_eventos_basket(*args, **kwargs) -> str:
    cards = build_event_cards()
    if not cards:
        if _view_handle_eventos_basket is not None:
            try:
                out = _view_handle_eventos_basket(*args, **kwargs)
                if isinstance(out, str):
                    return out
            except Exception:
                pass
        return "EVENTOS BASKET\n\nSin eventos disponibles."
    lines = ["EVENTOS BASKET", ""]
    for item in cards:
        title = item.get("title", "Partido")
        league = item.get("league", "Liga")
        start = item.get("start", "N/D")
        markets = item.get("markets", 0)
        lines.append(f"- {title} | {league} | {start} | mercados: {markets}")
    return "\n".join(lines)

def handle_basket_picks(*args, **kwargs) -> str:
    return "BASKET PICKS\n\nSin picks disponibles en la capa analitica."

__all__ = ["build_event_cards", "handle_eventos_basket", "handle_basket_picks"]
PYEOF

echo "[3/8] Compilando..."
if ! python3 -m py_compile "$FUTBOL" "$BASKET"; then
  rollback
  echo "ERROR: py_compile fallo"
  exit 1
fi

echo "[4/8] Smoke imports..."
if ! python3 - <<'PY'
from departments.deportes.futbol.handlers import handle_eventos_futbol, handle_futbol_picks
from departments.deportes.basket.handlers import handle_eventos_basket, handle_basket_picks
print("FUTBOL_OK", callable(handle_eventos_futbol), callable(handle_futbol_picks))
print("BASKET_OK", callable(handle_eventos_basket), callable(handle_basket_picks))
PY
then
  rollback
  echo "ERROR: smoke import fallo"
  exit 1
fi

echo "[5/8] Tests focales..."
pytest tests/providers/test_futbol_provider.py -v
pytest tests/repos/test_futbol_repo.py -v
pytest tests/services/test_futbol_service.py -v
pytest tests/providers/test_basket_provider.py -v
pytest tests/repos/test_basket_repo.py -v
pytest tests/services/test_basket_service.py -v

echo "[6/8] Tests globales..."
if ! pytest tests/ -v; then
  rollback
  echo "ERROR: pytest global fallo"
  exit 1
fi

echo "[7/8] Auditoria..."
if ! bash scripts/run_audit.sh; then
  rollback
  echo "ERROR: auditoria fallo"
  exit 1
fi

echo "[8/8] OK replicacion visual minima de futbol y basket aplicada"
