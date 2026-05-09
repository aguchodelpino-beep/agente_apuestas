from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from shared.datetime_utils import day_label, hour_label

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "data" / "cache_picks"

SPORT_HEADERS = {
    "futbol": "⚽ *FÚTBOL PICKS*",
    "basket": "🏀 *BASKET PICKS*",
    "tenis": "🎾 *TENIS PICKS*",
}


def _atomic_write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def _today() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d")


def _build_simple_pick(row: dict[str, Any], idx: int) -> dict[str, Any]:
    home = row.get("home_team") or row.get("home") or row.get("player_1") or row.get("competitor_1") or "TBD"
    away = row.get("away_team") or row.get("away") or row.get("player_2") or row.get("competitor_2") or "TBD"
    start = (
        row.get("commence_time")
        or row.get("start_time")
        or row.get("start")
        or row.get("date")
        or row.get("event_time")
        or row.get("scheduled")
        or ""
    )
    sport_key = row.get("_sport_key") or row.get("league") or row.get("tournament") or ""
    return {
        "index": idx,
        "match": f"{home} vs {away}",
        "start": start,
        "market": "Pendiente",
        "pick": "Sin modelo aún",
        "odds": "",
        "probability": "",
        "sport_key": sport_key,
    }


def build_picks_from_events(sport: str) -> int:
    src = ROOT / "data" / "raw" / sport / "latest.json"
    rows: list[dict[str, Any]] = []
    if src.exists():
        data = json.loads(src.read_text(encoding="utf-8"))
        if isinstance(data, list):
            rows = [x for x in data if isinstance(x, dict)]

    picks = [_build_simple_pick(row, i) for i, row in enumerate(rows[:15], start=1)]
    payload = {
        "sport": sport,
        "date": _today(),
        "count": len(picks),
        "items": picks,
    }

    _atomic_write(CACHE_DIR / f"{sport}_{_today()}.json", payload)
    _atomic_write(CACHE_DIR / f"{sport}_latest.json", payload)
    return len(picks)


def load_picks(sport: str) -> dict[str, Any]:
    path = CACHE_DIR / f"{sport}_latest.json"
    if not path.exists():
        return {"sport": sport, "date": _today(), "count": 0, "items": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {"sport": sport, "date": _today(), "count": 0, "items": []}
    except Exception:
        return {"sport": sport, "date": _today(), "count": 0, "items": []}


def render_picks(sport: str) -> str:
    data = load_picks(sport)
    items = data.get("items", [])
    if not items:
        return f"{SPORT_HEADERS.get(sport, '🎯 *PICKS*')}\n\nSin picks en cache de hoy."

    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        start = item.get("start") or ""
        day = day_label(start) if start else "Sin fecha"
        grouped.setdefault(day, []).append(item)

    lines = [SPORT_HEADERS.get(sport, "🎯 *PICKS*")]
    for day in sorted(grouped.keys()):
        lines.append("")
        lines.append(f"*{day}*")
        for item in grouped[day]:
            start = item.get("start") or ""
            hour = hour_label(start) if start else "--:--"
            line = f"{item.get('index')}. {hour} — {item.get('match')}"
            lines.append(line)

            meta = []
            if item.get("market"):
                meta.append(f"Mercado: {item['market']}")
            if item.get("pick"):
                meta.append(f"Pick: {item['pick']}")
            if item.get("odds"):
                meta.append(f"Cuota: {item['odds']}")
            if item.get("probability"):
                meta.append(f"Prob: {item['probability']}")
            if meta:
                lines.append("   " + " | ".join(meta))

    return "\n".join(lines)
