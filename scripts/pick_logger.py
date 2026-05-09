#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from departmentsdeportespickservice import generate_filtered_picks


def log_picks(liga: str, min_edge: float = 0.25, max_edge: float = 5.0) -> None:
    picks = generate_filtered_picks(liga, min_edge=min_edge, max_edge=max_edge, limit=50)
    
    history = Path("cachediario/picks_emitted_history.jsonl")
    history.parent.mkdir(parents=True, exist_ok=True)
    
    for pick in picks:
        pick_with_meta = {
            "emitted_at": "2026-05-07T03:10:00Z",  # Replace with real timestamp
            "liga": liga,
            **pick
        }
        history.write_text(json.dumps(pick_with_meta, ensure_ascii=False) + "\n",
                          mode="a", encoding="utf-8")
    
    print(f"Logged {len(picks)} {liga} picks to {history}")


if __name__ == "__main__":
    log_picks("NBA")
    log_picks("MLS")
