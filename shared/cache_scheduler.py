from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from shared.provider_theodds_api import get_active_tennis_keys, get_odds
from shared.picks_cache import build_picks_from_events
from scripts.build_enriched_cache import build_all as build_enriched_cache_all

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
CACHE_DIARIO_DIR = ROOT / "cache_diario"
TZ = "America/Guayaquil"

FOOTBALL_KEYS = [
    "soccer_epl",
    "soccer_spain_la_liga",
    "soccer_germany_bundesliga",
    "soccer_italy_serie_a",
    "soccer_france_ligue_one",
    "soccer_netherlands_eredivisie",
    "soccer_portugal_primeira_liga",
    "soccer_russia_premier_league",
    "soccer_uefa_champs_league",
    "soccer_uefa_europa_league",
    "soccer_uefa_europa_conference_league",
    "soccer_fa_cup",
    "soccer_germany_dfb_pokal",
    "soccer_italy_coppa_italia",
    "soccer_france_coupe_de_france",
    "soccer_brazil_campeonato",
    "soccer_argentina_primera_division",
    "soccer_mexico_ligamx",
    "soccer_colombia_primera_a",
    "soccer_chile_campeonato",
    "soccer_ecuador_liga_pro",
    "soccer_usa_mls",
    "soccer_saudi_arabia_pro_league",
    "soccer_japan_j_league",
    "soccer_china_superleague",
    "soccer_korea_kleague1",
    "soccer_australia_aleague",
    "soccer_uefa_champs_league",
    "soccer_conmebol_copa_libertadores",
    "soccer_conmebol_copa_sudamericana",
    "soccer_usa_mls",
]

BASKET_KEYS = [
    "basketball_nba",
    "basketball_wnba",
    "basketball_euroleague",
]

_scheduler: BackgroundScheduler | None = None


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)



def _today_str() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d")


def _atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    tmp.replace(path)


def _normalize_rows(rows: list[dict[str, Any]], sport_key: str, source: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        row = dict(row)
        row["_sport_key"] = sport_key
        row["_source"] = source
        out.append(row)
    return out


def _dedupe(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []

    for row in rows:
        key = str(
            row.get("id")
            or row.get("event_id")
            or f"{row.get('_sport_key','')}|{row.get('home_team','')}|{row.get('away_team','')}|{row.get('commence_time','')}"
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(row)

    out.sort(key=lambda x: x.get("commence_time") or "")
    return out


def _save_rows(sport: str, rows: list[dict[str, Any]]) -> Path:
    rows = _dedupe(rows)
    day = _today_str()
    out_path = RAW_DIR / sport / f"{day}.json"
    latest_path = RAW_DIR / sport / "latest.json"
    diario_path = CACHE_DIARIO_DIR / f"cache{sport}.json"

    CACHE_DIARIO_DIR.mkdir(parents=True, exist_ok=True)

    _atomic_write_json(out_path, rows)
    _atomic_write_json(latest_path, rows)
    _atomic_write_json(
        diario_path,
        {
            "sport": sport,
            "date": day,
            "updated_at": _utc_now().isoformat().replace("+00:00", "Z"),
            "items": rows,
        },
    )

    logger.info("cache %s guardado: %s eventos en %s", sport, len(rows), out_path)
    return out_path
def build_futbol_cache() -> int:
    rows: list[dict[str, Any]] = []
    for key in FOOTBALL_KEYS:
        try:
            rows.extend(_normalize_rows(get_odds(key, regions="us,eu", markets="h2h,spreads,totals"), key, "theodds"))
        except Exception as e:
            logger.warning("futbol %s error: %s", key, e)
    _save_rows("futbol", rows)
    return len(rows)


def build_basket_cache() -> int:
    rows: list[dict[str, Any]] = []
    for key in BASKET_KEYS:
        try:
            rows.extend(_normalize_rows(get_odds(key, regions="us,eu", markets="h2h,spreads,totals"), key, "theodds"))
        except Exception as e:
            logger.warning("basket %s error: %s", key, e)
    _save_rows("basket", rows)
    return len(rows)


def build_tenis_cache() -> int:
    rows: list[dict[str, Any]] = []
    try:
        tennis_keys = get_active_tennis_keys()
    except Exception as e:
        logger.warning("tenis sports error: %s", e)
        _save_rows("tenis", [])
        return 0

    for key in tennis_keys:
        try:
            rows.extend(_normalize_rows(get_odds(key, regions="us,eu", markets="h2h"), key, "theodds"))
        except Exception as e:
            logger.warning("tenis %s error: %s", key, e)
    _save_rows("tenis", rows)
    return len(rows)


def build_all_caches() -> dict[str, int]:
    result = {
        "futbol": build_futbol_cache(),
        "basket": build_basket_cache(),
        "tenis": build_tenis_cache(),
    }
    logger.info("cache diario completo: %s", result)
    return result


def build_all_pick_caches() -> dict[str, int]:
    result = {
        "futbol": build_picks_from_events("futbol"),
        "basket": build_picks_from_events("basket"),
        "tenis": build_picks_from_events("tenis"),
    }
    logger.info("cache picks completo: %s", result)
    return result


def ensure_today_cache_once() -> None:
    day = _today_str()
    needed = [
        RAW_DIR / "futbol" / f"{day}.json",
        RAW_DIR / "basket" / f"{day}.json",
        RAW_DIR / "tenis" / f"{day}.json",
    ]
    if any(not p.exists() for p in needed):
        logger.info("faltan caches de hoy; generando bootstrap")
        build_all_caches()

    build_all_pick_caches()


def start_cache_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    scheduler = BackgroundScheduler(timezone=TZ)
    scheduler.add_job(
        build_all_caches,
        CronTrigger(hour=2, minute=0, timezone=TZ),
        id="daily_cache_2am_ec",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
    )
    scheduler.add_job(
        build_enriched_cache_all,
        CronTrigger(hour=2, minute=5, timezone=TZ),
        id="daily_enriched_cache_205am_ec",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
    )
    scheduler.add_job(
        build_all_pick_caches,
        CronTrigger(hour=2, minute=10, timezone=TZ),
        id="daily_pick_cache_210am_ec",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
    )
    scheduler.start()

    ensure_today_cache_once()

    logger.info("scheduler cache iniciado: diario 02:00 %s", TZ)
    _scheduler = scheduler
    return scheduler

if __name__ == "__main__":
    print("SCRIPT OK")
