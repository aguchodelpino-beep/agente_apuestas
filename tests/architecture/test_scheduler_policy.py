from pathlib import Path

def test_shared_cache_scheduler_has_2am_job():
    text = Path("shared/cache_scheduler.py").read_text(encoding="utf-8")
    assert 'TZ = "America/Guayaquil"' in text
    assert 'CronTrigger(hour=2, minute=0, timezone=TZ)' in text
    assert 'id="daily_cache_2am_ec"' in text

def test_repos_never_call_live_apis():
    for rel in [
        "departments/deportes/futbol/repo.py",
        "departments/deportes/basket/repo.py",
        "departments/deportes/tenis/repo.py",
    ]:
        text = Path(rel).read_text(encoding="utf-8")
        forbidden = [
            "requests.",
            "httpx.",
            "urllib.",
            "provider_",
            "espn_get(",
            "get_odds(",
            "sportsgameodds",
            "rapidapi",
            "the-odds-api",
        ]
        for bad in forbidden:
            assert bad not in text, f"{rel} contiene acceso prohibido: {bad}"
