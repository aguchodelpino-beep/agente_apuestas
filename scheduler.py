from __future__ import annotations

from datetime import timezone
from pathlib import Path
import time

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from shared.cache import CacheManager
from shared.providers.tenis_provider import fetch_tennis_events
from shared.providers.futbol_provider import fetch_futbol_events
from shared.providers.basket_provider import fetch_basket_events

UTC = timezone.utc
cache = CacheManager()

def refresh_sport(sport: str) -> dict:
    started = time.perf_counter()
    error = None
    payload = []
    source = "unknown"
    try:
        if sport == "tenis":
            payload = fetch_tennis_events()
            source = "espn"
        elif sport == "futbol":
            payload = fetch_futbol_events()
            source = "openligadb"
        elif sport == "basket":
            payload = fetch_basket_events()
            source = "espn"
        else:
            raise ValueError(f"sport no soportado: {sport}")

        path = cache.write_day(sport, payload, source)
        status = "ok"
    except Exception as exc:
        status = "error"
        error = str(exc)
        path = cache.day_path(sport)

    p = Path(path)
    row = {
        "timestamp": cache.utc_now_iso() if hasattr(cache, "utc_now_iso") else None,
        "sport": sport,
        "status": status,
        "cache_status": "fresh" if status == "ok" else "error",
        "latency_ms": round((time.perf_counter() - started) * 1000, 2),
        "records": len(payload),
        "cache_path": str(path),
        "cache_file_size_bytes": p.stat().st_size if p.exists() else 0,
        "cache_age_minutes": 0.0,
        "error": error,
        "job_id": f"refresh_{sport}",
        "jobstore": "default",
        "source": source,
    }
    cache.write_metric(row)
    return row

def refresh_tenis() -> dict:
    return refresh_sport("tenis")

def refresh_futbol() -> dict:
    return refresh_sport("futbol")

def refresh_basket() -> dict:
    return refresh_sport("basket")

def build_scheduler() -> BackgroundScheduler:
    return BackgroundScheduler(
        jobstores={
            "default": SQLAlchemyJobStore(url="sqlite:///data/cache/scheduler/jobs.sqlite"),
            "memory": MemoryJobStore(),
        },
        timezone=UTC,
    )

def register_example_jobs(scheduler: BackgroundScheduler) -> None:
    # LEGACY DESACTIVADO: la política oficial usa shared/cache_scheduler.py
    # con build_all_caches() a las 02:00 America/Guayaquil.
    return None
def scheduler_summary(scheduler: BackgroundScheduler) -> list[dict]:
    started_here = False
    try:
        if not scheduler.running:
            scheduler.start(paused=True)
            started_here = True
        rows = []
        for job in scheduler.get_jobs():
            nrt = getattr(job, "next_run_time", None)
            rows.append({
                "id": getattr(job, "id", None),
                "name": getattr(job, "name", None),
                "jobstore": getattr(job, "_jobstore_alias", "default"),
                "next_run_time": nrt.isoformat() if nrt else None,
                "trigger": str(getattr(job, "trigger", "")),
            })
        return rows
    finally:
        if started_here and scheduler.running:
            scheduler.shutdown(wait=False)

if __name__ == "__main__":
    s = build_scheduler()
    register_example_jobs(s)
    s.start()
    print("scheduler_started")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        s.shutdown(wait=False)
