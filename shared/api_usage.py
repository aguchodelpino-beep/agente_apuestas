from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

USAGE_FILE = Path("cachediario/api_usage_history.jsonl")

API_LIMITS: dict[str, dict[str, Any]] = {
    "sportsgameodds": {"hourly": 1000, "daily": 24000, "cost_per_1000": 0.50},
    "oddsapi": {"hourly": 500, "daily": 5000, "cost_per_1000": 10.00},
    "pinnacle": {"hourly": 1000, "daily": None, "cost_per_1000": 1.00},
    "rapidapi": {"hourly": 1000, "daily": 10000, "cost_per_1000": 0.10},
    "api-sports": {"hourly": 1000, "daily": 100000, "cost_per_1000": 0.05},
}


def track_usage(
    source: str,
    used: int = 1,
    remaining: Optional[int] = None,
    total_limit: Optional[int] = None,
    endpoint: Optional[str] = None,
    status_code: Optional[int] = None,
) -> None:
    USAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "timestamp": datetime.now().isoformat(),
        "source": source,
        "used_today": used,
        "remaining": remaining,
        "limit": total_limit,
        "endpoint": endpoint,
        "status_code": status_code,
    }
    with USAGE_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_usage_history() -> list[dict]:
    if not USAGE_FILE.exists():
        return []
    rows: list[dict] = []
    with USAGE_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def build_daily_dashboard() -> dict[str, Any]:
    history = load_usage_history()
    today = datetime.now().strftime("%Y-%m-%d")
    today_usage: dict[str, int] = defaultdict(int)

    for row in history:
        ts = str(row.get("timestamp", ""))
        if ts.startswith(today):
            source = str(row.get("source", "unknown"))
            today_usage[source] += int(row.get("used_today", 0))

    report: dict[str, Any] = {}
    for source, used in today_usage.items():
        limits = API_LIMITS.get(source, {})
        daily_limit = limits.get("daily")
        pct = round((used / daily_limit * 100), 2) if daily_limit else None
        cost_today = round((used / 1000) * limits.get("cost_per_1000", 0.0), 4)

        report[source] = {
            "used_today": used,
            "daily_limit": daily_limit,
            "pct_used": pct,
            "cost_today_usd": cost_today,
            "estimated_monthly_cost_usd": round(cost_today * 30, 4),
            "warning": bool(pct is not None and pct > 80),
            "critical": bool(pct is not None and pct > 95),
        }

    report["summary"] = {
        "date": today,
        "total_sources": len([k for k in report.keys() if k != "summary"]),
        "total_used_today": sum(v["used_today"] for k, v in report.items() if k != "summary"),
        "total_cost_today_usd": round(
            sum(v["cost_today_usd"] for k, v in report.items() if k != "summary"), 4
        ),
    }
    return report

if __name__ == "__main__":
    print("SCRIPT OK")
