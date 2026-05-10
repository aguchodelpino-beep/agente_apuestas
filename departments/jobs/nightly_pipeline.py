"""
Nightly pipeline: fetch real data → normalize → write to data/raw/{sport}/{date}.json
Los repos leen de shared.cache.load_sport_day() que apunta a data/raw/
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

UTC = timezone.utc


def _to_legacy_row(ev: dict[str, Any], sport: str) -> dict[str, Any]:
    """Traduce formato nuevo (cache_diario) → formato legacy (data/raw) que leen los repos."""
    home = ev.get("home_team") or ev.get("home") or "TBD"
    away = ev.get("away_team") or ev.get("away") or "TBD"
    start = ev.get("datetime") or ev.get("start_time") or ev.get("date") or datetime.now(UTC).isoformat()
    league = (
        ev.get("league")
        or ev.get("tournament")
        or ev.get("_sport_key", "").replace("_", " ").title()
        or sport.title()
    )
    fixture_id = ev.get("id") or f"{home}-{away}-{start[:10]}"

    # Construir markets desde odds h2h
    odds = ev.get("odds", {})
    markets: list[dict] = []
    if odds:
        outcomes = [{"name": k, "price": v} for k, v in odds.items() if isinstance(v, (int, float))]
        if outcomes:
            markets.append({"key": "h2h", "outcomes": outcomes})

    # Agregar spread/OU de ESPN si existe
    espn_m = ev.get("espn_match") or {}
    espn_odds = espn_m.get("espn_odds", {}) if isinstance(espn_m, dict) else {}
    if espn_odds.get("spread"):
        markets.append({"key": "spreads", "espn_spread": espn_odds["spread"]})
    if espn_odds.get("over_under"):
        markets.append({"key": "totals", "espn_ou": espn_odds["over_under"]})

    return {
        "fixture_id": str(fixture_id),
        "sport": sport,
        "league": league,
        "home": home,
        "away": away,
        "start_time": start,
        "status": ev.get("status", "scheduled"),
        "source": ev.get("_source", "oddsapi"),
        "markets": markets,
        "raw": {
            "title": ev.get("title", f"{home} vs {away}"),
            "sport_key": ev.get("_sport_key", ""),
            "espn_match": ev.get("espn_match"),
        },
    }


def run(dry_run: bool = False) -> dict[str, Any]:
    from pathlib import Path as _Path
    from dotenv import load_dotenv
    load_dotenv(_Path(__file__).resolve().parents[3] / ".env")

    from shared.cache import save_sport_day
    from shared.datetime_utils import today_str
    from shared.providers.oddsapi_client import fetch_sport_group as odds_group
    from shared.providers.espn_client import fetch_sport_group as espn_group, crosscheck
    from shared.providers.balldontlie_client import fetch_fixtures as bdl_fetch
    from shared.cache_builder import build_sport_cache

    today = today_str()
    cache_dir = _Path("cache_diario")
    results: dict[str, Any] = {}

    for sport in ["basket", "futbol", "tenis"]:
        t0 = time.perf_counter()
        try:
            # 1. Fetch desde providers reales
            odds_events = bdl_fetch() if sport == "basket" else odds_group(sport)
            espn_events = espn_group(sport)

            # 2. Merge + crosscheck → cache_diario/
            all_events = build_sport_cache(
                sport, odds_events, espn_events, crosscheck, cache_dir
            )

            # 3. Traducir al formato legacy → data/raw/{sport}/{today}.json
            legacy_rows = [_to_legacy_row(ev, sport) for ev in all_events]
            if not dry_run:
                save_sport_day(sport, today, legacy_rows)

            elapsed = round(time.perf_counter() - t0, 2)
            results[sport] = {
                "status": "ok",
                "events": len(legacy_rows),
                "with_odds": sum(1 for r in legacy_rows if r["markets"]),
                "elapsed_s": elapsed,
            }
            print(f"  ✓ {sport}: {len(legacy_rows)} eventos ({elapsed}s)")
        except Exception as exc:
            results[sport] = {"status": "error", "error": str(exc)}
            print(f"  ✗ {sport}: {exc}")

    # 4. Guardar métricas del run
    metrics_path = _Path("data/monitoring") / "nightly_runs.jsonl"
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "timestamp": datetime.now(UTC).isoformat(),
        "date": today,
        "results": results,
    }
    if not dry_run:
        with metrics_path.open("a") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    return results


if __name__ == "__main__":
    print(f"[nightly_pipeline] {datetime.now(UTC).isoformat()}")
    results = run(dry_run=False)
    print(json.dumps(results, indent=2))
