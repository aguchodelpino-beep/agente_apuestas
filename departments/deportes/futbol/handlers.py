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
    try:
        from departments.deportes.futbol.analitica_picks_handlers import handle_futbol_picks_analitica
        return handle_futbol_picks_analitica()
    except Exception as e:
        return f"⚽ FUTBOL PICKS\n\nError al procesar picks: {e}"

__all__ = ["build_event_cards", "handle_eventos_futbol", "handle_futbol_picks"]

if __name__ == "__main__":
    print("SCRIPT OK")
