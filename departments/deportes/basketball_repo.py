from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from shared.clv import PickContext, enrich_pick_with_clv

BASE_PATH  = Path(__file__).parent.parent.parent
CACHE_DIR  = BASE_PATH / "cache_enriched"
HISTORY_DB = BASE_PATH / "data" / "history" / "odds_history.sqlite"


def _safe_float(v: Any) -> Optional[float]:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


# ── cache enriquecido ─────────────────────────────────────────────────────

def _load_cache_items() -> List[Dict[str, Any]]:
    path = CACHE_DIR / "cachebasket.json"
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return [x for x in payload["items"] if isinstance(x, dict)]
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    return []


def load_basket_events() -> List[Dict[str, Any]]:
    return _load_cache_items()


def get_basket_event_by_id(internal_event_id: str) -> Optional[Dict[str, Any]]:
    for evt in _load_cache_items():
        if evt.get("internal_event_id") == internal_event_id:
            return evt
    return None


# ── odds history snapshots ───────────────────────────────────────────────

def load_basket_snapshot_history(internal_event_id: str) -> List[Dict[str, Any]]:
    if not HISTORY_DB.exists():
        return []
    conn = _connect(HISTORY_DB)
    try:
        rows = conn.execute(
            """
            SELECT internal_event_id, sport, bookmaker,
                   market_key, outcome_key, outcome_name,
                   price, captured_at, event_date, raw_odd_id
            FROM odds_history
            WHERE internal_event_id = ?
            ORDER BY captured_at
            """,
            (internal_event_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ── CLV para picks ────────────────────────────────────────────────────────

def get_pick_clv_context(
    internal_event_id: str,
    *,
    bookmaker: str = "pinnacle",
    market_key: str,
    outcome_key: str,
) -> PickContext:
    if not HISTORY_DB.exists():
        return PickContext()
    snapshots = load_basket_snapshot_history(internal_event_id)
    if not snapshots:
        return PickContext()
    filtered = [
        r for r in snapshots
        if r.get("bookmaker") == bookmaker
        and r.get("market_key") == market_key
        and r.get("outcome_key") == outcome_key
    ]
    if not filtered:
        return PickContext()
    ordered = sorted(filtered, key=lambda r: str(r.get("captured_at") or ""))
    opening       = _safe_float(ordered[0].get("price"))
    closing       = _safe_float(ordered[-1].get("price"))
    opening_point = _safe_float(ordered[0].get("point")) if "point" in ordered[0] else None
    closing_point = _safe_float(ordered[-1].get("point")) if "point" in ordered[-1] else None
    return enrich_pick_with_clv(opening, closing, opening_point, closing_point)


def get_pick_enriched(
    internal_event_id: str,
    *,
    bookmaker: str = "pinnacle",
    market_key: str,
    outcome_key: str,
) -> Dict[str, Any]:
    clv = get_pick_clv_context(
        internal_event_id,
        bookmaker=bookmaker,
        market_key=market_key,
        outcome_key=outcome_key,
    )
    return dict(
        internal_event_id=internal_event_id,
        bookmaker=bookmaker,
        market_key=market_key,
        outcome_key=outcome_key,
        clv=clv,
    )
