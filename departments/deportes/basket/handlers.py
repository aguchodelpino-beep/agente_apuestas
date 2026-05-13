from __future__ import annotations

import json
from collections import OrderedDict
from datetime import datetime, timezone, timedelta
from pathlib import Path

_ECT = timezone(timedelta(hours=-5))  # Ecuador Time UTC-5
_JSON = Path("departments/deportes/basket/live_today.json")


def _safe_parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S+00:00",
                "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%MZ"):
        try:
            dt = datetime.strptime(value, fmt)
            # Si no tiene tzinfo asumimos UTC
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(_ECT)
        except Exception:
            pass
    return None


def _load_events() -> list[dict]:
    try:
        raw = json.loads(_JSON.read_text(encoding="utf-8"))
    except Exception:
        return []
    now = datetime.now(_ECT)
    result = []
    for ev in raw:
        status = str(ev.get("status", "")).lower()
        # Descartar finalizados explícitamente
        if any(s in status for s in ("final", "finished", "post", "complete")):
            continue
        dt = _safe_parse_dt(ev.get("datetime") or ev.get("start_time") or "")
        if dt is None:
            result.append(ev)
            continue
        # Mantener si: aún no empieza, o lleva menos de 3h desde el inicio
        if (now - dt).total_seconds() < 3 * 3600:
            result.append(ev)
    return result


def _group_lines(events: list[dict]) -> list[str]:
    grouped: OrderedDict[str, dict[str, list[str]]] = OrderedDict()
    for ev in events:
        dt = _safe_parse_dt(ev.get("datetime") or ev.get("start_time") or "")
        day_key = dt.strftime("%d/%m/%Y") if dt else "N/D"
        hour    = dt.strftime("%I:%M %p") if dt else "N/D"
        league  = ev.get("league", "Basketball")
        home    = ev.get("home", "?")
        away    = ev.get("away", "?")
        status  = str(ev.get("status", "")).lower()
        live    = " 🔴 EN VIVO" if "in" in status or "live" in status else ""
        line    = f"   🕐 {hour}{live} | {home} vs {away}"

        grouped.setdefault(day_key, {}).setdefault(league, []).append(line)

    lines: list[str] = []
    for day_key, leagues in grouped.items():
        lines.append(f"📅 {day_key}")
        for league, rows in leagues.items():
            emoji = "🏀" if league == "NBA" else "👟" if league == "WNBA" else "🏀"
            lines.append(f"  {emoji} {league}")
            lines.extend(rows)
        lines.append("")
    return lines


def build_event_cards(limit: int = 50) -> list[dict]:
    return _load_events()[:limit]


def handle_eventos_basket(*args, **kwargs) -> str:
    events = _load_events()
    now_ect = datetime.now(_ECT)
    lines = [
        "🏀 BASKET - PROXIMOS PARTIDOS",
        f"🗓️ {now_ect.strftime('%d/%m/%Y')}  🕐 ECT (UTC-5)",
        "━━━━━━━━━━━━━━━━━━━━━━",
        "",
    ]
    if events:
        lines.extend(_group_lines(events))
    else:
        lines.append("Sin eventos disponibles.")
        lines.append("")
    lines.append("📊 Ver picks con EV y Stake -> /basketpicks")
    return "\n".join(lines)


def handle_basket_picks(*args, **kwargs) -> str:
    try:
        from departments.deportes.basket.analitica_picks_handlers import handle_basket_picks_analitica
        return handle_basket_picks_analitica()
    except Exception as e:
        return f"🏀 BASKET PICKS\n\nError al procesar picks: {e}"


__all__ = ["build_event_cards", "handle_eventos_basket", "handle_basket_picks"]

if __name__ == "__main__":
    print("SCRIPT OK")
