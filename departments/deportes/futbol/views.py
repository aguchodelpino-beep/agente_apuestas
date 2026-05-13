import json
from pathlib import Path

JSON_PATH = Path("departments/deportes/futbol/live_today.json")

def handle_eventos_futbol():
    if not JSON_PATH.exists():
        return []
    try:
        rows = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []

    from datetime import datetime, timezone, timedelta
    _ECT = timezone(timedelta(hours=-5))
    now = datetime.now(_ECT)
    result = []
    for ev in rows:
        status = str(ev.get("status", "")).lower()
        if any(s in status for s in ("final", "finished", "post", "complete", "finalizado")):
            continue
        dt_str = str(ev.get("datetime") or ev.get("start_time") or "")
        if not dt_str or "T" not in dt_str:
            result.append(ev)
            continue
        try:
            s = dt_str.strip().replace("Z", "+00:00")
            dt = datetime.fromisoformat(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            dt_ect = dt.astimezone(_ECT)
            if (now - dt_ect).total_seconds() < 3 * 3600:
                result.append(ev)
        except Exception:
            result.append(ev)
    result.sort(key=lambda r: (0 if "in" in str(r.get("status","")).lower() else 1, r.get("datetime", "")))
    return result[:10]

if __name__ == "__main__":
    print("SCRIPT OK")
