from scheduler import build_scheduler, register_runtime_jobs, scheduler_summary


def test_register_runtime_jobs_adds_line_movement_alert():
    s = build_scheduler()
    try:
        register_runtime_jobs(s)
        rows = scheduler_summary(s)
        ids = {row["id"] for row in rows}
        assert "line_movement_alert" in ids
    finally:
        if s.running:
            s.shutdown(wait=False)
