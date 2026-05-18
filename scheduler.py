from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import time

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from departments.jobs.line_movement_alert import run_line_movement_alert
from shared.telegram_sender import send_telegram_message

UTC = timezone.utc
RAW_DIR = Path("data/raw")


class CacheManager:
    def utc_now_iso(self) -> str:
        return datetime.now(UTC).isoformat()

    def _today_str(self) -> str:
        return datetime.now(UTC).date().isoformat()

    def day_path(self, sport: str) -> Path:
        d = RAW_DIR / sport
        d.mkdir(parents=True, exist_ok=True)
        return d / f"{self._today_str()}.json"

    def read_day(self, sport: str) -> list:
        path = self.day_path(sport)
        if not path.exists():
            return []
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return []

    def write_metric(self, row: dict) -> Path:
        path = Path("data/cache/scheduler_metrics.jsonl")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        return path


cache = CacheManager()


def refresh_from_cache(sport: str) -> dict:
    started = time.perf_counter()
    payload = cache.read_day(sport)
    row = {
        "timestamp": cache.utc_now_iso(),
        "sport": sport,
        "status": "ok" if payload else "empty",
        "cache_status": "fresh" if payload else "missing",
        "latency_ms": round((time.perf_counter() - started) * 1000, 2),
        "records": len(payload),
        "cache_path": str(cache.day_path(sport)),
        "cache_age_minutes": 0.0,
        "job_id": f"refresh_{sport}_cache_only",
        "jobstore": "default",
        "source": "cache_only",
    }
    cache.write_metric(row)
    return row


def refresh_tenis() -> dict:
    return refresh_from_cache("tenis")


def refresh_futbol() -> dict:
    return refresh_from_cache("futbol")


def refresh_basket() -> dict:
    return refresh_from_cache("basket")


def build_scheduler() -> BackgroundScheduler:
    return BackgroundScheduler(
        jobstores={
            "default": SQLAlchemyJobStore(url="sqlite:///data/cache/scheduler/jobs.sqlite"),
            "memory": MemoryJobStore(),
        },
        timezone=UTC,
    )


def register_runtime_jobs(scheduler: BackgroundScheduler) -> None:
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

    for job_id, func, label in [
        ("refresh_tenis_cache", refresh_tenis, "Tenis – cache only"),
        ("refresh_futbol_cache", refresh_futbol, "Fútbol – cache only"),
        ("refresh_basket_cache", refresh_basket, "Basket – cache only"),
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
            next_run_time=datetime.now(UTC),
        )


if __name__ == "__main__":
    s = build_scheduler()
    register_runtime_jobs(s)
    s.start()
    print("scheduler_started_cache_only")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        s.shutdown(wait=False)

# ── alias para tests ──────────────────────────────────────────────────────────
# Los tests hacen: from scheduler import send_telegram_message
# La función real está en shared/telegram_sender.py — re-exportamos aquí.
try:
    from shared.telegram_sender import send_telegram_message as _stm  # noqa: F401
    send_telegram_message = _stm
except ImportError:
    import os, requests as _requests, logging as _logging
    _log = _logging.getLogger(__name__)
    def send_telegram_message(text: str) -> bool:  # type: ignore[misc]
        token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        if not token or not chat_id:
            _log.warning("send_telegram_message: variables no configuradas")
            return False
        try:
            resp = _requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
                timeout=10,
            )
            return resp.ok
        except Exception as exc:
            _log.error("send_telegram_message error: %s", exc)
            return False


def scheduler_summary(scheduler) -> list[dict]:
    """Retorna lista de jobs activos con id, name y próxima ejecución."""
    jobs = []
    for job in scheduler.get_jobs():
        next_run = getattr(job, "next_run_time", None)
        jobs.append({
            "id":       job.id,
            "name":     job.name,
            "next_run": str(next_run) if next_run else "not_started",
            "trigger":  str(job.trigger),
        })
    return jobs


def register_example_jobs(scheduler: BackgroundScheduler) -> None:
    """
    Función de documentación/onboarding.
    NO registra jobs reales — usa register_runtime_jobs() para eso.
    Los jobs de producción se registran en register_runtime_jobs.
    """
    pass
