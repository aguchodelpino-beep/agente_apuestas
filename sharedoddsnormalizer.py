from __future__ import annotations

from typing import Any


def parse_odd_id(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_sgo_odds(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "odd_id": parse_odd_id(row.get("odd_id") or row.get("id")),
        "fixture_id": str(row.get("fixture_id") or "").strip(),
        "market": str(row.get("market") or "").strip().lower(),
        "selection": str(row.get("selection") or "").strip().lower(),
        "odds": float(row.get("odds") or 0.0),
        "bookmaker": str(row.get("bookmaker") or "").strip().lower(),
        "raw": row,
    }
