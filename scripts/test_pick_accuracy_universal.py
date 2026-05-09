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
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
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

    return {
        "total_picks": total,
        "wins": wins,
        "losses": losses,
        "hit_rate_percent": round((wins / total * 100.0), 2) if total else 0.0,
        "profit_units": round(profit, 4),
        "roi_percent": round((profit / total * 100.0), 2) if total else 0.0,
    }


def main() -> None:
    sources = ["sportsgameodds", "oddsapi", "pinnacle"]  # Match logger sources
    
    all_reports = {}
    for source in sources:
        emitted = Path(f"cachediario/{source}_picks_resolved_history.jsonl")
        rows = load_jsonl(emitted)
        
        by_liga = defaultdict(list)
        by_book = defaultdict(list)
        by_bucket = defaultdict(list)
        by_live = defaultdict(list)

        for r in rows:
            by_liga[str(r.get("liga", "unknown"))].append(r)
            by_book[str(r.get("bookmaker", "unknown"))].append(r)
            by_bucket[edge_bucket(float(r.get("edge_percent", 0.0)))].append(r)
            by_live["live" if r.get("live") else "pregame"].append(r)

        report = {
            "provider": source,
            "overall": summarize(rows),
            "by_liga": {k: summarize(v) for k, v in sorted(by_liga.items())},
            "by_bookmaker": {k: summarize(v) for k, v in sorted(by_book.items())},
            "by_edge_bucket": {k: summarize(v) for k, v in sorted(by_bucket.items())},
            "by_live_state": {k: summarize(v) for k, v in sorted(by_live.items())},
        }
        all_reports[source] = report
        
        print(f"\n=== {source.upper()} ===")
        print(json.dumps(report["overall"], ensure_ascii=False, indent=2))

    # Global report
    out = Path("cachediario/all_providers_accuracy_report.json")
    out.write_text(json.dumps(all_reports, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nGLOBAL_REPORT: {out}")


if __name__ == "__main__":
    main()
