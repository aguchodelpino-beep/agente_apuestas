#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scheduler import refresh_sport
from shared.cache import CacheManager

cache = CacheManager()

def refresh_cmd(sport: str) -> None:
    print(json.dumps(refresh_sport(sport), ensure_ascii=False, indent=2))

def status_cmd() -> None:
    path = cache.metrics_path()
    if not path.exists():
        print(json.dumps({"status": "empty_metrics"}, ensure_ascii=False, indent=2))
        return
    rows = json.loads(path.read_text(encoding="utf-8"))
    latest = {}
    for row in rows:
        latest[row["sport"]] = row
    print(json.dumps(latest, ensure_ascii=False, indent=2))

def prune_cmd(days: int) -> None:
    removed = []
    for sport_dir in Path("data/raw").glob("*"):
        if not sport_dir.is_dir():
            continue
        files = sorted(sport_dir.glob("*.json"))
        if len(files) <= days:
            continue
        for f in files[:-days]:
            f.unlink(missing_ok=True)
            removed.append(str(f))
    print(json.dumps({"removed": removed, "count": len(removed)}, ensure_ascii=False, indent=2))

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("refresh")
    a.add_argument("sport", choices=["tenis", "futbol", "basket"])

    sub.add_parser("status")

    c = sub.add_parser("prune")
    c.add_argument("--days", type=int, default=7)

    args = parser.parse_args()
    if args.cmd == "refresh":
        refresh_cmd(args.sport)
    elif args.cmd == "status":
        status_cmd()
    elif args.cmd == "prune":
        prune_cmd(args.days)

if __name__ == "__main__":
    main()
