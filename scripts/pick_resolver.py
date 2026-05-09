#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


def resolve_picks() -> None:
    emitted = Path("cachediario/picks_emitted_history.jsonl")
    resolved = Path("cachediario/picks_resolved_history.jsonl")
    
    if not emitted.exists():
        print("No emitted picks found")
        return
    
    # Simulate resolution (replace with real results API)
    results_map = {
        "bH0jpRCUT3RgQEUqQsD5": "win",  # Cincinnati won
        "kHFvte8smrc7rzupzCZ7": "loss",  # Timberwolves lost?
    }
    
    resolved_rows = []
    for line in emitted.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        pick = json.loads(line)
        event_id = pick.get("event_id")
        result = results_map.get(event_id, "pending")
        pick["result"] = result
        resolved_rows.append(pick)
    
    resolved.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in resolved_rows) + "\n",
                       encoding="utf-8")
    
    print(f"Resolved {len(resolved_rows)} picks to {resolved}")


if __name__ == "__main__":
    resolve_picks()
