import json
from pathlib import Path
from departments.deportes import tenis_repo as repo


def test_load_tenis_events_reads_fixed_cache(tmp_path: Path, monkeypatch):
    cache_dir = tmp_path / "cache_enriched"
    cache_dir.mkdir()
    (cache_dir / "cachetenis.json").write_text(
        json.dumps({
            "sport": "tenis",
            "updated_at": "2026-05-10T08:00:00Z",
            "window_days": 3,
            "items": [{"internal_event_id": "evt_ten_1"}],
        }),
        encoding="utf-8",
    )
    monkeypatch.setattr(repo, "CACHE_DIR", cache_dir)
    events = repo.load_tenis_events()
    assert len(events) == 1
    assert events[0]["internal_event_id"] == "evt_ten_1"
