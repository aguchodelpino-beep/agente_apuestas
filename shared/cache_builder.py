"""Builder central de cache diario — merge Odds-API + ESPN fallback."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any


def build_sport_cache(
    sport: str,
    odds_events: List[Dict[str, Any]],
    espn_events: List[Dict[str, Any]],
    crosscheck_fn,
    cache_dir: Path,
) -> List[Dict[str, Any]]:
    enriched       = crosscheck_fn(odds_events, espn_events)
    covered        = {e["title"] for e in enriched}
    espn_only      = []
    for ev in espn_events:
        if ev["title"] not in covered:
            ev["espn_match"] = {
                "espn_id":     ev.get("id"),
                "espn_status": ev.get("status"),
                "espn_odds":   ev.get("espn_odds", {}),
            }
            ev.setdefault("_source", "espn_only")
            ev.setdefault("odds", {})
            espn_only.append(ev)
    all_events = enriched + espn_only
    out = {
        "sport":      sport,
        "date":       datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
        "items":      all_events,
    }
    cache_dir.mkdir(exist_ok=True)
    (cache_dir / f"cache{sport}.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2)
    )
    return all_events

if __name__ == "__main__":
    print("SCRIPT OK")
