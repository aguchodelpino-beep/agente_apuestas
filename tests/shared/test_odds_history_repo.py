from __future__ import annotations

import json
from pathlib import Path

from shared.odds_history_repo import (
    ensure_schema,
    extract_snapshots_from_enriched_event,
    ingest_enriched_directory,
    ingest_enriched_file,
    insert_snapshots,
    load_snapshots_for_event,
    point_to_key,
)


def make_enriched_event() -> dict:
    return {
        "internal_event_id": "evt_test_123",
        "sport": "futbol",
        "league": "Premier League",
        "start_time": "2026-05-09T19:00:00Z",
        "home_team": "Liverpool",
        "away_team": "Chelsea",
        "bookmakers": [
            {
                "key": "pinnacle",
                "title": "Pinnacle",
                "markets": [
                    {
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Liverpool", "price": 1.88},
                            {"name": "Chelsea", "price": 3.75},
                            {"name": "Draw", "price": 4.00},
                        ],
                    },
                    {
                        "key": "spreads",
                        "outcomes": [
                            {"name": "Liverpool", "price": 1.95, "point": -0.5},
                            {"name": "Chelsea", "price": 1.90, "point": 0.5},
                        ],
                    },
                ],
            }
        ],
    }


def test_point_to_key():
    assert point_to_key(None) == "__none__"
    assert point_to_key(-0.5) == "-0.5"
    assert point_to_key("0.5") == "0.5"


def test_extract_snapshots_from_enriched_event():
    event = make_enriched_event()
    rows = extract_snapshots_from_enriched_event(
        event,
        snapshot_time="2026-05-09T18:00:00Z",
        source_file="cache_enriched/futbol_2026-05-09.json",
    )

    assert len(rows) == 5
    assert rows[0]["internal_event_id"] == "evt_test_123"
    assert rows[0]["bookmaker_key"] == "pinnacle"
    assert rows[0]["snapshot_time"] == "2026-05-09T18:00:00Z"


def test_insert_and_load_snapshots(tmp_path: Path):
    db_path = tmp_path / "odds_history.sqlite"
    ensure_schema(db_path)

    rows = extract_snapshots_from_enriched_event(
        make_enriched_event(),
        snapshot_time="2026-05-09T18:00:00Z",
        source_file="sample.json",
    )
    inserted = insert_snapshots(db_path, rows)

    loaded = load_snapshots_for_event(db_path, "evt_test_123")

    assert inserted == 5
    assert len(loaded) == 5
    assert loaded[0]["internal_event_id"] == "evt_test_123"


def test_insert_snapshots_is_idempotent(tmp_path: Path):
    db_path = tmp_path / "odds_history.sqlite"
    rows = extract_snapshots_from_enriched_event(
        make_enriched_event(),
        snapshot_time="2026-05-09T18:00:00Z",
        source_file="sample.json",
    )

    first = insert_snapshots(db_path, rows)
    second = insert_snapshots(db_path, rows)

    loaded = load_snapshots_for_event(db_path, "evt_test_123")

    assert first == 5
    assert second == 0
    assert len(loaded) == 5


def test_ingest_enriched_file(tmp_path: Path):
    db_path = tmp_path / "odds_history.sqlite"
    enriched_file = tmp_path / "futbol_2026-05-09.json"
    enriched_file.write_text(json.dumps([make_enriched_event()]), encoding="utf-8")

    inserted = ingest_enriched_file(
        db_path,
        enriched_file,
        snapshot_time="2026-05-09T18:00:00Z",
    )

    loaded = load_snapshots_for_event(db_path, "evt_test_123")

    assert inserted == 5
    assert len(loaded) == 5


def test_ingest_enriched_directory_filters_by_sport(tmp_path: Path):
    db_path = tmp_path / "odds_history.sqlite"
    enriched_dir = tmp_path / "cache_enriched"
    enriched_dir.mkdir()

    (enriched_dir / "futbol_2026-05-09.json").write_text(
        json.dumps([make_enriched_event()]),
        encoding="utf-8",
    )

    tennis_event = make_enriched_event()
    tennis_event["internal_event_id"] = "evt_tenis_1"
    tennis_event["sport"] = "tenis"
    (enriched_dir / "tenis_2026-05-09.json").write_text(
        json.dumps([tennis_event]),
        encoding="utf-8",
    )

    inserted = ingest_enriched_directory(
        db_path,
        enriched_dir,
        sport="futbol",
        snapshot_time="2026-05-09T18:00:00Z",
    )

    futbol_rows = load_snapshots_for_event(db_path, "evt_test_123")
    tenis_rows = load_snapshots_for_event(db_path, "evt_tenis_1")

    assert inserted == 5
    assert len(futbol_rows) == 5
    assert len(tenis_rows) == 0
