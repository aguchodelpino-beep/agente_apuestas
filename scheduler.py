from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import time

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from departments.jobs.line_movement_alert import run_line_movement_alert
from shared.providers.tenis_provider import fetch_tennis_events
from shared.providers.futbol_provider import fetch_futbol_events
from shared.providers.basket_provider import fetch_basket_events

from shared import cache as cache_mod
from shared.telegram_sender import send_telegram_message

UTC = timezone.utc


class CacheManager:
    def utc_now_iso(self) -> str:
        return datetime.now(UTC).isoformat()

    def _today_str(self) -> str:
        return datetime.now(UTC).date().isoformat()

    def day_path(self, sport: str) -> Path:
        d = cache_mod.RAW_DIR / sport
        d.mkdir(parents=True, exist_ok=True)
        return d / f"{self._today_str()}.json"

    def write_day(self, sport: str, payload: list, source: str = "unknown") -> Path:
        path = self.day_path(sport)
        cache_mod.write_json(path, payload)
        return path

    def write_metric(self, row: dict) -> Path:
        path = cache_mod.SCHEDULER_DIR / "scheduler_metrics.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        return path


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
        "timestamp": cache.utc_now_iso(),
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
    return None


def _refresh_basket_with_json() -> dict:
    """Refresca basket y actualiza live_today.json con filtro ECT."""
    import json
    from pathlib import Path
    result = refresh_sport("basket")
    try:
        events = fetch_basket_events()
        rows = [
            {
                "id": e["fixture_id"],
                "home": e["home"],
                "away": e["away"],
                "datetime": e["start_time"],
                "league": e["league"],
                "status": e["status"],
                "_source": e["source"],
            }
            for e in events
        ]
        out = Path("departments/deportes/basket/live_today.json")
        out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as exc:
        result["live_today_error"] = str(exc)
    return result


def register_runtime_jobs(scheduler: BackgroundScheduler) -> None:
    # Alertas de movimiento de línea
    scheduler.add_job(
        run_line_movement_alert,
        trigger="interval",
        hours=1,
        id="line_movement_alert",
        name="Line movement alert",
        jobstore="default",
        kwargs={"send_fn": send_telegram_message},
        replace_existing=True,
        coalesce=True,
        max_instances=1,
        misfire_grace_time=900,
    )
    # Refresco de deportes cada 30 min
    for job_id, func, label in [
        ("refresh_tenis",  refresh_tenis,              "Tenis – refresh ESPN"),
        ("refresh_futbol", refresh_futbol,             "Fútbol – refresh OpenLigaDB"),
        ("refresh_basket", _refresh_basket_with_json,  "Basket – refresh ESPN + live_today.json"),
    ]:
        scheduler.add_job(
            func,
            trigger="interval",
            minutes=30,
            id=job_id,
            name=label,
            jobstore="default",
            replace_existing=True,
            coalesce=True,
            max_instances=1,
            misfire_grace_time=300,
        )


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
    register_runtime_jobs(s)
    s.start()
    print("scheduler_started")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        s.shutdown(wait=False)
