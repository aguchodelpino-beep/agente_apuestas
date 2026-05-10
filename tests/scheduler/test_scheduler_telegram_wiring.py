import scheduler


def test_register_runtime_jobs_wires_telegram_sender():
    s = scheduler.build_scheduler()
    try:
        scheduler.register_runtime_jobs(s)
        job = s.get_job("line_movement_alert")
        assert job is not None
        assert job.kwargs["send_fn"] is scheduler.send_telegram_message
    finally:
        if s.running:
            s.shutdown(wait=False)
