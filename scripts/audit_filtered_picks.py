#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from departmentsdeportespickservice import generate_filtered_picks


def audit_picks() -> None:
    thresholds = [0.25, 0.50, 1.00]
    ligas = ["NBA", "MLS"]

    report: dict = {
        "timestamp": datetime.now().isoformat(),
        "thresholds": thresholds,
        "ligas": ligas,
        "picks_by_threshold": {},
        "stats": {
            "total_candidates": 0,
            "avg_edge": 0.0,
            "top_books": {},
        },
    }

    unique_picks: dict[tuple, dict] = {}

    for liga in ligas:
        for edge in thresholds:
            picks = generate_filtered_picks(liga, min_edge=edge, limit=20)
            key = f"{liga}_edge_{edge:.2f}"
            report["picks_by_threshold"][key] = picks

            for p in picks:
                uniq_key = (
                    p.get("event_id"),
                    p.get("best_side"),
                    p.get("bookmaker"),
                    p.get("book_odds"),
                )
                if uniq_key not in unique_picks:
                    unique_picks[uniq_key] = p

    all_unique = list(unique_picks.values())

    report["stats"]["total_candidates"] = len(all_unique)

    if all_unique:
        edges = [float(p.get("edge_percent", 0.0)) for p in all_unique]
        report["stats"]["avg_edge"] = round(sum(edges) / len(edges), 4)

        top_books: dict[str, int] = {}
        for p in all_unique:
            book = str(p.get("bookmaker", "unknown"))
            top_books[book] = top_books.get(book, 0) + 1

        report["stats"]["top_books"] = dict(
            sorted(top_books.items(), key=lambda x: x[1], reverse=True)
        )

    out = Path("cachediario/sgo_filtered_picks_audit.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("AUDIT_FILE:", out)
    print("=" * 80)

    for key, picks in report["picks_by_threshold"].items():
        print(f"{key}: {len(picks)} picks")
        for item in picks[:3]:
            print(
                f"  {item['match']} | {item['best_side'].upper()} | "
                f"{item['bookmaker']} | edge={item['edge_percent']:.2f}%"
            )

    print("\nSTATS:")
    print(f"Candidatos únicos total: {report['stats']['total_candidates']}")
    print(f"Edge promedio: {report['stats']['avg_edge']:.2f}%")
    print(f"Top books: {report['stats']['top_books']}")


if __name__ == "__main__":
    audit_picks()
