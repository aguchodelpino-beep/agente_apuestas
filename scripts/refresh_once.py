#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.cache_scheduler import build_all_caches, build_all_pick_caches

def main() -> int:
    result_events = build_all_caches()
    result_picks = build_all_pick_caches()
    print({"events": result_events, "picks": result_picks})
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
