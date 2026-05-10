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

    rows = [r for r in rows if str(r.get("status", "")).lower() != "finalizado"]
    rows.sort(key=lambda r: (0 if "EN VIVO" in str(r.get("status", "")) else 1, r.get("datetime", "")))
    return rows[:10]
