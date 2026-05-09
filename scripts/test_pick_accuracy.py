#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

def american_profit_units(odd: str) -> float:
    s = str(odd).strip()
    if s.startswith("+"):
        return float(s[1:]) / 100.0
    if s.startswith("-"):
        return 100.0 / abs(float(s))
    return 0.0

def main() -> None:
    path = Path("fixtures/picks_results_sample.json")
    rows = json.loads(path.read_text(encoding="utf-8"))

    total = len(rows)
    wins = sum(1 for r in rows if r["result"] == "win")
    losses = sum(1 for r in rows if r["result"] == "loss")

    stake = 1.0
    profit = 0.0
    for r in rows:
        if r["result"] == "win":
            profit += american_profit_units(r["book_odds"]) * stake
        elif r["result"] == "loss":
            profit -= stake

    hit_rate = (wins / total * 100.0) if total else 0.0
    roi = (profit / total * 100.0) if total else 0.0

    report = {
        "total_picks": total,
        "wins": wins,
        "losses": losses,
        "hit_rate_percent": round(hit_rate, 2),
        "profit_units": round(profit, 4),
        "roi_percent": round(roi, 2),
    }

    out = Path("cachediario/pick_accuracy_report.json")
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
