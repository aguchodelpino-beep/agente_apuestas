from pathlib import Path

import shared.cache_scheduler as cs


def test_official_scheduler_source_has_expected_jobs():
    text = Path("shared/cache_scheduler.py").read_text(encoding="utf-8")
    assert 'id="daily_cache_2am_ec"' in text
    assert "CronTrigger(hour=2, minute=0, timezone=TZ)" in text
    assert 'id="daily_pick_cache_210am_ec"' in text
    assert "CronTrigger(hour=2, minute=10, timezone=TZ)" in text


def test_start_cache_scheduler_registers_only_official_jobs(monkeypatch):
    monkeypatch.setattr(cs, "ensure_today_cache_once", lambda: None)

    scheduler = cs.start_cache_scheduler()
    try:
        ids = sorted(job.id for job in scheduler.get_jobs() if job.id)
        assert "daily_cache_2am_ec" in ids
        assert "daily_pick_cache_210am_ec" in ids
        assert not any("refresh_" in job_id for job_id in ids)
        assert not any("legacy" in job_id.lower() for job_id in ids)
    finally:
        scheduler.shutdown(wait=False)
