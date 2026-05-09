from pathlib import Path

def test_scheduler_register_example_jobs_has_no_add_job_calls():
    text = Path("scheduler.py").read_text(encoding="utf-8")
    start = text.find("def register_example_jobs(scheduler: BackgroundScheduler) -> None:")
    assert start != -1, "No existe register_example_jobs"
    tail = text[start:]
    next_def = tail.find("\ndef ", 1)
    block = tail if next_def == -1 else tail[:next_def]
    assert "add_job(" not in block, "register_example_jobs no debe registrar jobs legacy"

def test_official_cache_scheduler_keeps_2am_job():
    text = Path("shared/cache_scheduler.py").read_text(encoding="utf-8")
    assert 'CronTrigger(hour=2, minute=0, timezone=TZ)' in text
    assert 'id="daily_cache_2am_ec"' in text
