#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from departmentsdeportespickservice import generate_filtered_picks


def save_historical_pick(pick: dict, filename: Path) -> None:
    """Append pick to historical JSONL file."""
    pick_with_ts = {
        "timestamp": datetime.now().isoformat(),
        **pick
    }
    filename.parent.mkdir(parents=True, exist_ok=True)
    filename.write_text(json.dumps(pick_with_ts, ensure_ascii=False) + "\n", 
                       mode="a", encoding="utf-8")


def audit_picks(ligas: list[str], 
                thresholds: list[float],
                live_only: bool,
                min_edge: float,
                save_history: bool) -> None:
    
    report: dict = {
        "timestamp": datetime.now().isoformat(),
        "ligas": ligas,
        "thresholds": thresholds,
        "live_only": live_only,
        "min_edge": min_edge,
        "picks_by_liga": {},
        "stats": {
            "total_candidates": 0,
            "avg_edge": 0.0,
            "by_bookmaker": {},
            "by_sport": {},
        }
    }

    all_picks = []
    history_file = Path("cachediario/sgo_picks_history.jsonl")

    for liga in ligas:
        liga_picks = []
        for edge in thresholds:
            picks = generate_filtered_picks(
                liga, 
                min_edge=edge, 
                limit=50
            )
            
            for pick in picks:
                # Filtro live_only
                if live_only and pick.get("live"):
                    continue
                    
                # Filtro min_edge global
                if pick.get("edge_percent", 0) < min_edge:
                    continue
                
                liga_picks.append(pick)
                all_picks.append(pick)
                
                if save_history:
                    save_historical_pick(pick, history_file)

        report["picks_by_liga"][liga] = liga_picks

    # Stats
    report["stats"]["total_candidates"] = len(all_picks)
    
    if all_picks:
        edges = [p["edge_percent"] for p in all_picks]
        report["stats"]["avg_edge"] = round(sum(edges) / len(edges), 4)
        
        # Por bookmaker
        by_book = {}
        for p in all_picks:
            book = p["bookmaker"]
            by_book[book] = by_book.get(book, 0) + 1
        report["stats"]["by_bookmaker"] = dict(
            sorted(by_book.items(), key=lambda x: x[1], reverse=True)
        )
        
        # Por deporte
        by_sport = {}
        for p in all_picks:
            sport = p.get("liga", "unknown")
            by_sport[sport] = by_sport.get(sport, 0) + 1
        report["stats"]["by_sport"] = by_sport

    # Save report
    out = Path("cachediario/sgo_filtered_picks_audit.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # Print summary
    print("AUDIT_FILE:", out)
    print("HISTORY_FILE:", history_file)
    print("=" * 80)

    for liga, picks in report["picks_by_liga"].items():
        print(f"{liga}: {len(picks)} picks")
        for item in sorted(picks, key=lambda x: x["edge_percent"], reverse=True)[:5]:
            print(f"  {item['match']} | {item['best_side'].upper()} | "
                  f"{item['bookmaker']} | edge={item['edge_percent']:.2f}%")

    print("\nSTATS:")
    print(f"Candidatos únicos: {report['stats']['total_candidates']}")
    print(f"Edge promedio: {report['stats']['avg_edge']:.2f}%")
    print(f"Por book: {report['stats']['by_bookmaker']}")
    print(f"Por deporte: {report['stats']['by_sport']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit SportsGameOdds picks")
    parser.add_argument("--ligas", nargs="+", default=["NBA", "MLS"],
                       help="Ligas a auditar (default: NBA MLS)")
    parser.add_argument("--thresholds", nargs="+", type=float, 
                       default=[0.25, 0.50, 1.00],
                       help="Umbrales de edge a probar")
    parser.add_argument("--live-only", action="store_true",
                       help="Solo eventos live")
    parser.add_argument("--min-edge", type=float, default=0.25,
                       help="Edge mínimo global")
    parser.add_argument("--no-history", action="store_true",
                       help="No guardar histórico JSONL")
    
    args = parser.parse_args()
    
    audit_picks(
        ligas=args.ligas,
        thresholds=args.thresholds,
        live_only=args.live_only,
        min_edge=args.min_edge,
        save_history=not args.no_history
    )


if __name__ == "__main__":
    main()
