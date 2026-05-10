"""
Scheduler nocturno (no sustituye tu scheduler.py actual).
Corre un solo job diario a las 11:00 UTC.
"""
from datetime import datetime, timezone

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger


def run_nightly_pipeline():
    from departments.jobs.nightly_pipeline import run as nightly_run
    nightly_run(dry_run=False)


def main():
    # Usa UTC para que el job siempre dispare a 11:00 UTC
    scheduler = BlockingScheduler(timezone="UTC")

    # 11:00 UTC todos los días
    cron = CronTrigger(
        hour=11,       # 11 de la mañana
        minute=0,      # en punto
        second=0,      # exacto
        timezone="UTC",
    )

    scheduler.add_job(
        func=run_nightly_pipeline,
        trigger=cron,
        id="nightly_pipeline_job",
        name="Nightly cache + ingest (agente_apuestas)",
        replace_existing=True,
    )

    print(f"[{datetime.now(timezone.utc).isoformat()}] Scheduler nocturno iniciado…")
    scheduler.start()


if __name__ == "__main__":
    main()
