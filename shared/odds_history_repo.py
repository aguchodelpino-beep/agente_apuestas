from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def point_to_key(point: Any) -> str:
    if point is None:
        return "__none__"
    if isinstance(point, float):
        return f"{point:.6f}".rstrip("0").rstrip(".") if "." in f"{point:.6f}" else f"{point:.6f}"
    return str(point).strip()


def ensure_schema(db_path: str | Path) -> None:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS odds_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                internal_event_id TEXT NOT NULL,
                sport TEXT NOT NULL,
                bookmaker_key TEXT NOT NULL,
                market_key TEXT NOT NULL,
                outcome_name TEXT NOT NULL,
                price REAL,
                point REAL,
                point_key TEXT NOT NULL DEFAULT '__none__',
                event_start_time TEXT,
                snapshot_time TEXT NOT NULL,
                source_file TEXT
            )
            """
        )

        columns = {
            row[1]
            for row in conn.execute("PRAGMA table_info(odds_snapshots)").fetchall()
        }
        if "point_key" not in columns:
            conn.execute(
                "ALTER TABLE odds_snapshots ADD COLUMN point_key TEXT NOT NULL DEFAULT '__none__'"
            )

        conn.execute(
            """
            UPDATE odds_snapshots
            SET point_key = CASE
                WHEN point IS NULL THEN '__none__'
                ELSE TRIM(CAST(point AS TEXT))
            END
            WHERE point_key IS NULL OR point_key = ''
            """
        )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_odds_event
            ON odds_snapshots(internal_event_id)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_odds_sport
            ON odds_snapshots(sport)
            """
        )
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS uq_odds_snapshot_dedupe
            ON odds_snapshots(
                internal_event_id,
                bookmaker_key,
                market_key,
                outcome_name,
                point_key,
                snapshot_time
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def extract_snapshots_from_enriched_event(
    event: dict[str, Any],
    *,
    snapshot_time: str | None = None,
    source_file: str | None = None,
) -> list[dict[str, Any]]:
    snapshot_time = snapshot_time or utc_now_iso()
    internal_event_id = event.get("internal_event_id")
    sport = event.get("sport", "unknown")
    event_start_time = event.get("start_time")
    bookmakers = event.get("bookmakers") or []

    rows: list[dict[str, Any]] = []

    for bookmaker in bookmakers:
        bookmaker_key = bookmaker.get("key") or bookmaker.get("title") or "unknown_bookmaker"
        for market in bookmaker.get("markets") or []:
            market_key = market.get("key") or "unknown_market"
            for outcome in market.get("outcomes") or []:
                point = outcome.get("point")
                rows.append(
                    {
                        "internal_event_id": internal_event_id,
                        "sport": sport,
                        "bookmaker_key": bookmaker_key,
                        "market_key": market_key,
                        "outcome_name": outcome.get("name") or "unknown_outcome",
                        "price": outcome.get("price"),
                        "point": point,
                        "point_key": point_to_key(point),
                        "event_start_time": event_start_time,
                        "snapshot_time": snapshot_time,
                        "source_file": source_file,
                    }
                )

    return rows


def insert_snapshots(db_path: str | Path, snapshots: list[dict[str, Any]]) -> int:
    if not snapshots:
        return 0

    ensure_schema(db_path)
    conn = sqlite3.connect(str(db_path))
    inserted = 0

    try:
        for row in snapshots:
            point = row.get("point")
            point_key = row.get("point_key") or point_to_key(point)

            cur = conn.execute(
                """
                INSERT OR IGNORE INTO odds_snapshots (
                    internal_event_id,
                    sport,
                    bookmaker_key,
                    market_key,
                    outcome_name,
                    price,
                    point,
                    point_key,
                    event_start_time,
                    snapshot_time,
                    source_file
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["internal_event_id"],
                    row["sport"],
                    row["bookmaker_key"],
                    row["market_key"],
                    row["outcome_name"],
                    row.get("price"),
                    point,
                    point_key,
                    row.get("event_start_time"),
                    row["snapshot_time"],
                    row.get("source_file"),
                ),
            )
            inserted += cur.rowcount

        conn.commit()
        return inserted
    finally:
        conn.close()


def load_snapshots_for_event(
    db_path: str | Path,
    internal_event_id: str,
) -> list[dict[str, Any]]:
    ensure_schema(db_path)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT
                internal_event_id,
                sport,
                bookmaker_key,
                market_key,
                outcome_name,
                price,
                point,
                point_key,
                event_start_time,
                snapshot_time,
                source_file
            FROM odds_snapshots
            WHERE internal_event_id = ?
            ORDER BY snapshot_time ASC, bookmaker_key ASC, market_key ASC, outcome_name ASC
            """,
            (internal_event_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def ingest_enriched_file(
    db_path: str | Path,
    enriched_file: str | Path,
    *,
    snapshot_time: str | None = None,
) -> int:
    path = Path(enriched_file)
    events = json.loads(path.read_text(encoding="utf-8"))
    total_inserted = 0

    for event in events:
        snapshots = extract_snapshots_from_enriched_event(
            event,
            snapshot_time=snapshot_time,
            source_file=str(path),
        )
        total_inserted += insert_snapshots(db_path, snapshots)

    return total_inserted


def ingest_enriched_directory(
    db_path: str | Path,
    enriched_dir: str | Path,
    *,
    sport: str | None = None,
    snapshot_time: str | None = None,
) -> int:
    path = Path(enriched_dir)
    total_inserted = 0

    pattern = f"{sport}_*.json" if sport else "*.json"
    for enriched_file in sorted(path.glob(pattern)):
        total_inserted += ingest_enriched_file(
            db_path,
            enriched_file,
            snapshot_time=snapshot_time,
        )

    return total_inserted

if __name__ == "__main__":
    print("SCRIPT OK")
