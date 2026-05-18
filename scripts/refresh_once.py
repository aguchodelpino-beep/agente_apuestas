#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv()

from scripts.refresh_multi_provider import build_daily_events
from shared.picks_cache import build_picks_from_events


def main() -> int:
    required = ["ODDSAPI_KEYS", "TAVILY_API_KEY"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        print(json.dumps({"ok": False, "missing": missing}, ensure_ascii=False), file=sys.stderr)
        return 1

    events = build_daily_events()
    picks = {
        "futbol": build_picks_from_events("futbol"),
        "basket": build_picks_from_events("basket"),
        "tenis": build_picks_from_events("tenis"),
    }
    print(json.dumps({"ok": True, "events": events, "picks": picks}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
