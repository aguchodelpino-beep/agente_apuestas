from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

EC = ZoneInfo("America/Guayaquil")

def _fmt_time(value: str | None) -> str:
    if not value:
        return "--:--"
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.astimezone(EC).strftime("%d/%m %I:%M %p")
    except Exception:
        return str(value)

def _status_emoji(status: str | None) -> str:
    s = (status or "").lower()
    if s == "live":
        return "🔴 EN VIVO"
    if s == "finished":
        return "✅ FINALIZADO"
    return "🕒"

def format_event_list(title: str, rows: list[dict]) -> str:
    if not rows:
        return f"{title}\n\nSin eventos disponibles."
    out = [title, ""]
    for i, ev in enumerate(rows, 1):
        out.append(f"{i}. {_status_emoji(ev.get('status'))}  {_fmt_time(ev.get('start_time'))}")
        out.append(f"   {ev.get('home', 'TBD')} vs {ev.get('away', 'TBD')}")
        out.append(f"   {ev.get('league', 'Sin liga')}")
        out.append("")
    return "\n".join(out).strip()
