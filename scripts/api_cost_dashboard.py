#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from shared.api_usage import build_daily_dashboard


def main() -> None:
    report = build_daily_dashboard()

    print("=== API COST DASHBOARD ===")
    print()
    print("| Provider | Used | Limit | % Used | Cost | Monthly |")
    print("|---|---:|---:|---:|---:|---:|")

    for source, data in sorted(report.items()):
        if source == "summary":
            continue
        pct = "N/A" if data["pct_used"] is None else f'{data["pct_used"]}%'
        limit = "N/A" if data["daily_limit"] is None else str(data["daily_limit"])
        print(
            f"| {source} | {data['used_today']} | {limit} | {pct} | "
            f"${data['cost_today_usd']:.4f} | ${data['estimated_monthly_cost_usd']:.4f} |"
        )

    print()
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))

    out = Path("cachediario/api_cost_dashboard.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"REPORT_FILE: {out}")


if __name__ == "__main__":
    main()
