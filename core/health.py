from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from core.config import settings


@dataclass
class HealthStatus:
    ok: bool
    timezone: str
    cache_dir: str
    scheduler_runs_file: str
    scheduler_runs_exists: bool
    scheduler_jobs_file: str
    scheduler_jobs_exists: bool
    stale_files: list[str]


def _is_stale(path: Path, *, max_age_minutes: int) -> bool:
    if not path.exists():
        return True
    modified = datetime.fromtimestamp(path.stat().st_mtime)
    age = datetime.now() - modified
    return age > timedelta(minutes=max_age_minutes)


def get_health_status(max_age_minutes: int = 360) -> dict[str, Any]:
    cache_dir = settings.cache_dir
    scheduler_dir = cache_dir / "scheduler"
    runs_file = scheduler_dir / "runs.json"
    jobs_file = scheduler_dir / "active_jobs.json"

    stale_files: list[str] = []
    for sport in ("futbol", "tenis", "basket"):
        p = settings.base_dir / "data" / "raw" / sport
        if not p.exists():
            stale_files.append(str(p))
            continue
        files = sorted(p.glob("*.json"))
        if not files:
            stale_files.append(str(p))
            continue
        newest = files[-1]
        if _is_stale(newest, max_age_minutes=max_age_minutes):
            stale_files.append(str(newest))

    ok = runs_file.exists() and jobs_file.exists() and len(stale_files) == 0

    status = HealthStatus(
        ok=ok,
        timezone=settings.timezone,
        cache_dir=str(cache_dir),
        scheduler_runs_file=str(runs_file),
        scheduler_runs_exists=runs_file.exists(),
        scheduler_jobs_file=str(jobs_file),
        scheduler_jobs_exists=jobs_file.exists(),
        stale_files=stale_files,
    )
    return asdict(status)
