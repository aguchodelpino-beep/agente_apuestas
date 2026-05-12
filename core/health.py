from __future__ import annotations

import sqlite3
import urllib.request
import urllib.error
from dataclasses import asdict, dataclass, field
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
    db_status: dict = field(default_factory=dict)
    api_status: dict = field(default_factory=dict)


def _is_stale(path: Path, *, max_age_minutes: int) -> bool:
    if not path.exists():
        return True
    modified = datetime.fromtimestamp(path.stat().st_mtime)
    age = datetime.now() - modified
    return age > timedelta(minutes=max_age_minutes)


def check_db(db_path: str) -> dict:
    try:
        conn = sqlite3.connect(db_path, timeout=3)
        conn.execute("SELECT 1")
        conn.close()
        return {"ok": True, "path": db_path, "error": None}
    except Exception as e:
        return {"ok": False, "path": db_path, "error": str(e)}


def check_api_url(url: str, timeout: int = 5) -> dict:
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return {"ok": resp.status < 500, "status": resp.status, "url": url, "error": None}
    except urllib.error.HTTPError as e:
        ok = e.code < 500
        return {"ok": ok, "status": e.code, "url": url, "error": str(e)}
    except Exception as e:
        return {"ok": False, "status": None, "url": url, "error": str(e)}


def get_health_status(
    max_age_minutes: int = 360,
    check_dbs: list[str] | None = None,
    check_apis: list[str] | None = None,
) -> dict[str, Any]:
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

    # DB checks
    db_results: dict = {}
    default_dbs = check_dbs or [
        str(settings.base_dir / "data" / "history" / "bets_history.sqlite"),
        str(settings.base_dir / "data" / "history" / "clv_smoke.sqlite"),
    ]
    for db_path in default_dbs:
        db_results[Path(db_path).name] = check_db(db_path)

    # API checks (solo si se pasan explícitamente para no golpear APIs en tests)
    api_results: dict = {}
    for url in (check_apis or []):
        api_results[url] = check_api_url(url)

    db_ok = all(v["ok"] for v in db_results.values())
    ok = (
        runs_file.exists()
        and jobs_file.exists()
        and len(stale_files) == 0
        and db_ok
    )

    status = HealthStatus(
        ok=ok,
        timezone=settings.timezone,
        cache_dir=str(cache_dir),
        scheduler_runs_file=str(runs_file),
        scheduler_runs_exists=runs_file.exists(),
        scheduler_jobs_file=str(jobs_file),
        scheduler_jobs_exists=jobs_file.exists(),
        stale_files=stale_files,
        db_status=db_results,
        api_status=api_results,
    )
    return asdict(status)
