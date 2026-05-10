from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

BASE_PATH = Path(__file__).resolve().parent.parent
CACHE_DIR = BASE_PATH / "cache_enriched"
WINDOW_DAYS = 3

SPORT_CONFIG = {
    "basket": "cachebasket.json",
    "futbol": "cachefutbol.json",
    "tenis": "cachetenis.json",
}

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def _parse_date(value: str | None):
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            dt = datetime.strptime(value, fmt)
            return dt.date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except Exception:
        return None

def _event_date(item: Dict[str, Any]):
    for key in ("event_date", "start_date", "commence_date", "date"):
        parsed = _parse_date(item.get(key))
        if parsed is not None:
            return parsed
    for key in ("event_start_time", "commence_time", "start_time", "datetime"):
        parsed = _parse_date(item.get(key))
        if parsed is not None:
            return parsed
    return None

def _within_window(item: Dict[str, Any], today):
    d = _event_date(item)
    if d is None:
        return False
    return today <= d <= (today + timedelta(days=WINDOW_DAYS - 1))

def _event_id(item: Dict[str, Any]) -> str:
    return str(
        item.get("internal_event_id")
        or item.get("event_id")
        or item.get("id")
        or ""
    ).strip()

def _sort_key(item: Dict[str, Any]):
    return (
        str(item.get("event_date") or ""),
        str(item.get("event_start_time") or item.get("commence_time") or ""),
        _event_id(item),
    )

def _load_existing(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return [x for x in payload["items"] if isinstance(x, dict)]
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    return []

def _write_cache(path: Path, sport: str, items: List[Dict[str, Any]]) -> None:
    payload = {
        "sport": sport,
        "updated_at": utc_now_iso(),
        "window_days": WINDOW_DAYS,
        "items": items,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

def _merge_items(old_items: Iterable[Dict[str, Any]], new_items: Iterable[Dict[str, Any]], today) -> List[Dict[str, Any]]:
    merged: Dict[str, Dict[str, Any]] = {}
    for item in list(old_items) + list(new_items):
        if not isinstance(item, dict):
            continue
        eid = _event_id(item)
        if not eid:
            continue
        if not _within_window(item, today):
            continue
        merged[eid] = item
    return sorted(merged.values(), key=_sort_key)

def _collect_source_items_for_sport(sport: str) -> List[Dict[str, Any]]:
    candidates = [
        BASE_PATH / "cache" / f"{sport}.json",
        BASE_PATH / "cache" / f"{sport}_today.json",
        BASE_PATH / "cache_diario" / f"{sport}.json",
        BASE_PATH / "cache_diario" / f"{sport}_today.json",
        BASE_PATH / "data" / sport / "live_today.json",
        BASE_PATH / "departments" / "deportes" / sport / "live_today.json",
    ]
    for path in candidates:
        if path.exists():
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(payload, list):
                    return [x for x in payload if isinstance(x, dict)]
                if isinstance(payload, dict) and isinstance(payload.get("items"), list):
                    return [x for x in payload["items"] if isinstance(x, dict)]
            except Exception:
                continue
    return []

def build_cache_for_sport(sport: str, *, today=None) -> Path:
    if sport not in SPORT_CONFIG:
        raise ValueError(f"unsupported sport: {sport}")
    today = today or datetime.now(timezone.utc).date()
    path = CACHE_DIR / SPORT_CONFIG[sport]
    existing = _load_existing(path)
    incoming = _collect_source_items_for_sport(sport)
    merged = _merge_items(existing, incoming, today)
    _write_cache(path, sport, merged)
    return path

def build_all(*, today=None) -> List[Path]:
    return [build_cache_for_sport(s, today=today) for s in SPORT_CONFIG]

if __name__ == "__main__":
    paths = build_all()
    for p in paths:
        print(p)
