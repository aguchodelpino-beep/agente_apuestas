#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


def american_profit_units(odd: str) -> float:
    s = str(odd).strip()
    if s.startswith("+"):
        return float(s[1:]) / 100.0
    if s.startswith("-"):
        return 100.0 / abs(float(s))
    return 0.0


def edge_bucket(edge: float) -> str:
    if edge < 0.25:
        return "<0.25"
    if edge < 0.50:
        return "0.25-0.49"
    if edge < 1.00:
        return "0.50-0.99"
    return "1.00+"


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def summarize(rows: list[dict]) -> dict:
    total = len(rows)
    wins = sum(1 for r in rows if r.get("result") == "win")
    losses = sum(1 for r in rows if r.get("result") == "loss")

    profit = 0.0
    for r in rows:
        odd = str(r.get("book_odds", ""))
        if r.get("result") == "win":
            profit += american_profit_units(odd)
        elif r.get("result") == "loss":
            profit -= 1.0

    hit_rate = round((wins / total * 100.0), 2) if total else 0.0
    roi = round((profit / total * 100.0), 2) if total else 0.0

    return {
        "total_picks": total,
        "wins": wins,
        "losses": losses,
        "hit_rate_percent": hit_rate,
        "profit_units": round(profit, 4),
        "roi_percent": roi,
    }


def main() -> None:
    path = Path("cachediario/picks_resolved_history.jsonl")
    rows = load_jsonl(path)

    overall = summarize(rows)

    by_liga: dict[str, list[dict]] = defaultdict(list)
    by_book: dict[str, list[dict]] = defaultdict(list)
    by_bucket: dict[str, list[dict]] = defaultdict(list)
    by_live: dict[str, list[dict]] = defaultdict(list)

    for r in rows:
        by_liga[str(r.get("liga", "unknown"))].append(r)
        by_book[str(r.get("bookmaker", "unknown"))].append(r)
        by_bucket[edge_bucket(float(r.get("edge_percent", 0.0)))].append(r)
        by_live["live" if r.get("live") else "pregame"].append(r)

    report = {
        "overall": overall,
        "by_liga": {k: summarize(v) for k, v in sorted(by_liga.items())},
        "by_bookmaker": {k: summarize(v) for k, v in sorted(by_book.items())},
        "by_edge_bucket": {k: summarize(v) for k, v in sorted(by_bucket.items())},
        "by_live_state": {k: summarize(v) for k, v in sorted(by_live.items())},
    }

    out = Path("cachediario/pick_accuracy_report_v2.json")
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(report["overall"], ensure_ascii=False, indent=2))
    print("REPORT_FILE:", out)


if __name__ == "__main__":
    main()
