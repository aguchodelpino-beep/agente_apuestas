from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BASE_DIR = Path(".").resolve()
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
CACHE_DIR = DATA_DIR / "cache"
SCHEDULER_DIR = CACHE_DIR / "scheduler"

for p in [DATA_DIR, RAW_DIR, CACHE_DIR, SCHEDULER_DIR]:
    p.mkdir(parents=True, exist_ok=True)


def _sport_file(sport: str, day: str) -> Path:
    d = RAW_DIR / sport
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{day}.json"


def load_sport_day(sport: str, day: str) -> list[dict[str, Any]]:
    path = _sport_file(sport, day)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_sport_day(sport: str, day: str, items: list[dict[str, Any]]) -> None:
    path = _sport_file(sport, day)
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    print("SCRIPT OK")

# Alias de compatibilidad
class CacheManager:
    load = staticmethod(load_sport_day)
    save = staticmethod(save_sport_day)
    write = staticmethod(write_json)

# Re-export de compatibilidad
from shared.datetime_utils import today_str  # noqa: F401
