import json
from datetime import date
from pathlib import Path
from scripts import build_enriched_cache as mod

def test_build_cache_fixed_filename_and_3day_window(tmp_path: Path, monkeypatch):
    base = tmp_path
    monkeypatch.setattr(mod, "BASE_PATH", base)
    monkeypatch.setattr(mod, "CACHE_DIR", base / "cache_enriched")

    src = base / "cache" / "basket.json"
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text(json.dumps([
        {"internal_event_id": "a", "event_date": "2026-05-10"},
        {"internal_event_id": "b", "event_date": "2026-05-11"},
        {"internal_event_id": "c", "event_date": "2026-05-12"},
        {"internal_event_id": "d", "event_date": "2026-05-13"},
        {"internal_event_id": "old", "event_date": "2026-05-09"},
    ]), encoding="utf-8")

    out = mod.build_cache_for_sport("basket", today=date(2026, 5, 10))
    payload = json.loads(out.read_text(encoding="utf-8"))
    ids = [x["internal_event_id"] for x in payload["items"]]

    assert out.name == "cachebasket.json"
    assert payload["sport"] == "basket"
    assert payload["window_days"] == 3
    assert ids == ["a", "b", "c"]
