#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/aguchodelpino/agente_apuestas"
cd "$PROJECT_DIR"

FILES=(
  "departments/deportes/futbol/handlers.py"
  "departments/deportes/basket/handlers.py"
  "departments/deportes/tenis/handlers.py"
)

TMPDIR="$(mktemp -d)"
cleanup() {
  rm -rf "$TMPDIR"
}
trap cleanup EXIT

for f in "${FILES[@]}"; do
  [ -f "$f" ] || { echo "ERROR: falta $f"; exit 1; }
  cp "$f" "$TMPDIR/$(basename "$f").bak"
done

rollback() {
  echo
  echo "[ROLLBACK] Restaurando handlers originales..."
  cp "$TMPDIR/handlers.py.bak" departments/deportes/futbol/handlers.py 2>/dev/null || true
}

mkdir -p shared

echo "[1/7] Creando catalogo central de ligas..."
cat > shared/sports_leagues_catalog.py <<'PYEOF'
from __future__ import annotations

FUTBOL_ALLOWED_LEAGUES = {
    "soccer_epl": "Premier League (Inglaterra)",
    "soccer_spain_la_liga": "La Liga (Espana)",
    "soccer_germany_bundesliga": "Bundesliga (Alemania)",
    "soccer_italy_serie_a": "Serie A (Italia)",
    "soccer_france_ligue_one": "Ligue 1 (Francia)",
    "soccer_netherlands_eredivisie": "Eredivisie (Holanda)",
    "soccer_portugal_primeira_liga": "Primeira Liga (Portugal)",
    "soccer_russia_premier_league": "Premier League (Rusia)",
    "soccer_uefa_champs_league": "Champions League",
    "soccer_uefa_europa_league": "Europa League",
    "soccer_uefa_europa_conference_league": "Conference League",
    "soccer_fa_cup": "FA Cup",
    "soccer_germany_dfb_pokal": "DFB Pokal",
    "soccer_italy_coppa_italia": "Coppa Italia",
    "soccer_france_coupe_de_france": "Coupe de France",
    "soccer_brazil_campeonato": "Serie A (Brasil)",
    "soccer_argentina_primera_division": "Primera Division (Argentina)",
    "soccer_mexico_ligamx": "Liga MX (Mexico)",
    "soccer_colombia_primera_a": "Primera A (Colombia)",
    "soccer_chile_campeonato": "Primera Division (Chile)",
    "soccer_ecuador_liga_pro": "LigaPro (Ecuador)",
    "soccer_conmebol_copa_libertadores": "Copa Libertadores",
    "soccer_conmebol_copa_sudamericana": "Copa Sudamericana",
    "soccer_usa_mls": "MLS (USA)",
    "soccer_saudi_arabia_pro_league": "Saudi Pro League",
    "soccer_japan_j_league": "J League (Japon)",
    "soccer_china_superleague": "Super League (China)",
    "soccer_korea_kleague1": "K League 1 (Corea)",
    "soccer_australia_aleague": "A-League (Australia)",
}

BASKET_ALLOWED_LEAGUES = {
    "basketball_nba": "NBA",
    "basketball_euroleague": "Euroleague",
    "basketball_wnba": "WNBA",
}
PYEOF

echo "[2/7] Reescribiendo handlers futbol..."
cat > departments/deportes/futbol/handlers.py <<'PYEOF'
from __future__ import annotations

from collections import OrderedDict
from datetime import datetime
from departments.deportes.futbol.views import handle_eventos_futbol as _view_handle_eventos_futbol

def _safe_parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except Exception:
            pass
    return None

def build_event_cards(limit: int = 50) -> list[dict]:
    try:
        data = _view_handle_eventos_futbol()
        if isinstance(data, list):
            return data[:limit]
    except Exception:
        pass
    return []

def _group_lines(cards: list[dict]) -> list[str]:
    grouped: OrderedDict[str, list[str]] = OrderedDict()
    for item in cards:
        title = item.get("title", "Partido")
        start = item.get("start") or item.get("date") or ""
        dt = _safe_parse_dt(start)
        day_key = dt.strftime("%d/%m") if dt else "N/D"
        hour = dt.strftime("%I:%M %p") if dt else "N/D"
        status = str(item.get("status", "")).lower()
        live = " 🔴 EN VIVO" if "live" in status or "en vivo" in status else ""
        line = f"   🕐 {hour}{live} | {title}"
        grouped.setdefault(day_key, []).append(line)

    lines: list[str] = []
    for day_key, rows in grouped.items():
        lines.append(f"📅 {day_key}")
        lines.extend(rows)
        lines.append("")
    return lines

def handle_eventos_futbol(*args, **kwargs) -> str:
    cards = build_event_cards()
    today = datetime.utcnow().strftime("%d/%m/%Y")
    lines = [
        "⚽ FUTBOL - PROXIMOS PARTIDOS",
        f"🗓️ {today}",
        "━━━━━━━━━━━━━━━━━━━━━━",
        "",
    ]
    if cards:
        lines.extend(_group_lines(cards))
    else:
        lines.append("Sin eventos disponibles.")
        lines.append("")
    lines.append("📊 Ver picks con EV y Stake -> /futbolpicks")
    return "\n".join(lines)

def handle_futbol_picks(*args, **kwargs) -> str:
    return "⚽ FUTBOL PICKS\n\nSin picks disponibles en la capa analitica."

__all__ = ["build_event_cards", "handle_eventos_futbol", "handle_futbol_picks"]
PYEOF

echo "[3/7] Reescribiendo handlers basket..."
cat > departments/deportes/basket/handlers.py <<'PYEOF'
from __future__ import annotations

from collections import OrderedDict
from datetime import datetime
from departments.deportes.basket.views import handle_eventos_basket as _view_handle_eventos_basket

def _safe_parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except Exception:
            pass
    return None

def build_event_cards(limit: int = 50) -> list[dict]:
    try:
        data = _view_handle_eventos_basket()
        if isinstance(data, list):
            return data[:limit]
    except Exception:
        pass
    return []

def _group_lines(cards: list[dict]) -> list[str]:
    grouped: OrderedDict[str, list[str]] = OrderedDict()
    for item in cards:
        title = item.get("title", "Partido")
        start = item.get("start") or item.get("date") or ""
        dt = _safe_parse_dt(start)
        day_key = dt.strftime("%d/%m") if dt else "N/D"
        hour = dt.strftime("%I:%M %p") if dt else "N/D"
        status = str(item.get("status", "")).lower()
        live = " 🔴 EN VIVO" if "live" in status or "en vivo" in status else ""
        line = f"   🕐 {hour}{live} | {title}"
        grouped.setdefault(day_key, []).append(line)

    lines: list[str] = []
    for day_key, rows in grouped.items():
        lines.append(f"📅 {day_key}")
        lines.extend(rows)
        lines.append("")
    return lines

def handle_eventos_basket(*args, **kwargs) -> str:
    cards = build_event_cards()
    today = datetime.utcnow().strftime("%d/%m/%Y")
    lines = [
        "🏀 BASKET - PROXIMOS PARTIDOS",
        f"🗓️ {today}",
        "━━━━━━━━━━━━━━━━━━━━━━",
        "",
    ]
    if cards:
        lines.extend(_group_lines(cards))
    else:
        lines.append("Sin eventos disponibles.")
        lines.append("")
    lines.append("📊 Ver picks con EV y Stake -> /basketpicks")
    return "\n".join(lines)

def handle_basket_picks(*args, **kwargs) -> str:
    return "🏀 BASKET PICKS\n\nSin picks disponibles en la capa analitica."

__all__ = ["build_event_cards", "handle_eventos_basket", "handle_basket_picks"]
PYEOF

echo "[4/7] Reescribiendo handlers tenis..."
cat > departments/deportes/tenis/handlers.py <<'PYEOF'
from __future__ import annotations

from collections import OrderedDict
from datetime import datetime
from departments.deportes.tenis.views import handle_eventos_tenis as _view_handle_eventos_tenis
from departments.deportes.tenis.views import handle_tenis_picks as _view_handle_tenis_picks

def _safe_parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except Exception:
            pass
    return None

def build_event_cards(limit: int = 50) -> list[dict]:
    try:
        data = _view_handle_eventos_tenis()
        if isinstance(data, list):
            return data[:limit]
    except Exception:
        pass
    return []

def _group_lines(cards: list[dict]) -> list[str]:
    grouped: OrderedDict[str, list[str]] = OrderedDict()
    for item in cards:
        title = item.get("title", "Partido")
        start = item.get("start") or item.get("date") or ""
        dt = _safe_parse_dt(start)
        day_key = dt.strftime("%d/%m") if dt else "N/D"
        hour = dt.strftime("%I:%M %p") if dt else "N/D"
        status = str(item.get("status", "")).lower()
        live = " 🔴 EN VIVO" if "live" in status or "en vivo" in status else ""
        line = f"   🕐 {hour}{live} | {title}"
        grouped.setdefault(day_key, []).append(line)

    lines: list[str] = []
    for day_key, rows in grouped.items():
        lines.append(f"📅 {day_key}")
        lines.extend(rows)
        lines.append("")
    return lines

def handle_eventos_tenis(*args, **kwargs) -> str:
    cards = build_event_cards()
    today = datetime.utcnow().strftime("%d/%m/%Y")
    lines = [
        "🎾 TENIS - PROXIMOS PARTIDOS",
        f"🗓️ {today}",
        "━━━━━━━━━━━━━━━━━━━━━━",
        "",
    ]
    if cards:
        lines.extend(_group_lines(cards))
    else:
        lines.append("Sin eventos disponibles.")
        lines.append("")
    lines.append("📊 Ver picks con EV y Stake -> /tenispicks")
    return "\n".join(lines)

def handle_tenis_picks(*args, **kwargs) -> str:
    try:
        out = _view_handle_tenis_picks(*args, **kwargs)
        if isinstance(out, str):
            return out
    except Exception:
        pass
    return "🎾 TENIS PICKS\n\nSin picks disponibles en la capa analitica."

__all__ = ["build_event_cards", "handle_eventos_tenis", "handle_tenis_picks"]
PYEOF

echo "[5/7] Compilando..."
python3 -m py_compile \
  shared/sports_leagues_catalog.py \
  departments/deportes/futbol/handlers.py \
  departments/deportes/basket/handlers.py \
  departments/deportes/tenis/handlers.py

echo "[6/7] Smoke test..."
python3 - <<'PY'
from departments.deportes.futbol.handlers import handle_eventos_futbol
from departments.deportes.basket.handlers import handle_eventos_basket
from departments.deportes.tenis.handlers import handle_eventos_tenis

print(handle_eventos_futbol()[:500])
print("-----")
print(handle_eventos_basket()[:500])
print("-----")
print(handle_eventos_tenis()[:500])
PY

echo "[7/7] Tests..."
pytest tests/ -v
python -m unittest discover -s tests -v

echo
echo "OK: formato de eventos y catalogo de ligas aplicado"
