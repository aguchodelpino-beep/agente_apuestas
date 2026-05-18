from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from departments.visuales.formatter import format_events_block

ROOT = Path(__file__).resolve().parent
DATA_RAW = ROOT / "data" / "raw"
EC_TZ = ZoneInfo("America/Guayaquil")
UTC = timezone.utc

SPORT_PATHS = {
    "tenis": DATA_RAW / "tenis" / "latest.json",
    "futbol": DATA_RAW / "futbol" / "latest.json",
    "basket": DATA_RAW / "basket" / "latest.json",
}

LIVE_STATUSES = {"live", "inplay", "in_progress", "1h", "2h", "ht", "et", "bt", "q1", "q2", "q3", "q4", "int"}
FINISHED_STATUSES = {"finished", "final", "ft", "aet", "pen", "ended", "complete", "completed", "closed"}
HIDDEN_STATUSES = FINISHED_STATUSES | {"cancelled", "canceled", "postponed"}

SPORT_HEADERS = {
    "tenis": ("Tenis", "🎾", "tenispicks"),
    "futbol": ("Fútbol", "⚽", "futbolpicks"),
    "basket": ("Basket", "🏀", "basketpicks"),
}

LIVE_WINDOW_BY_SPORT = {
    "futbol": timedelta(hours=3),
    "basket": timedelta(hours=3),
    "tenis": timedelta(hours=4),
}


def _now_ec() -> datetime:
    return datetime.now(EC_TZ)


def _parse_dt(value: str) -> datetime | None:
    if not value:
        return None
    try:
        s = value.strip().replace("Z", "+00:00")
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt.astimezone(EC_TZ)
    except Exception:
        return None


def _raw_status(row: dict) -> str:
    status = str(row.get("status") or "").strip().lower()
    if row.get("live") is True:
        return "live"
    return status


def _is_finished(status: str) -> bool:
    return status in HIDDEN_STATUSES


def _infer_live(row: dict, sport: str, dt: datetime | None, status: str) -> bool:
    if status in LIVE_STATUSES:
        return True
    if _is_finished(status):
        return False
    if row.get("live") is True:
        return True
    if not dt:
        return False

    now = _now_ec()
    live_window = LIVE_WINDOW_BY_SPORT[sport]
    return dt <= now <= dt + live_window


def _display_status(is_live: bool) -> str:
    return "🔴 EN VIVO" if is_live else ""


def _display_datetime(dt: datetime | None) -> str:
    if not dt:
        return ""
    return dt.strftime("%Y-%m-%dT%H:%M")


def _canonical_league(league: str) -> str:
    mapping = {
        "basketball_nba": "NBA",
        "basketball_wnba": "WNBA",
        "basketball_euroleague": "EuroLeague",
    }
    return mapping.get(league, league)


def _dedupe_bucket(item: dict) -> str:
    dt = item.get("_sort_dt")
    day_key = dt.strftime("%Y-%m-%d") if dt else ""
    home = str(item.get("home") or "").strip().lower()
    away = str(item.get("away") or "").strip().lower()
    league = str(item.get("league") or "").strip().lower()
    return f"{home}|{away}|{league}|{day_key}"


def _normalize_event(row: dict, sport: str) -> dict:
    dt = _parse_dt(
        row.get("commence_time") or row.get("start_time") or row.get("date") or row.get("datetime") or ""
    )
    status = _raw_status(row)
    is_live = _infer_live(row, sport, dt, status)

    league = row.get("league") or row.get("tournament") or row.get("competition") or row.get("sport_key") or "N/A"
    league = _canonical_league(str(league))

    return {
        "datetime": _display_datetime(dt),
        "home": row.get("home") or row.get("home_team") or row.get("team1") or "TBD",
        "away": row.get("away") or row.get("away_team") or row.get("team2") or "TBD",
        "league": league,
        "status": _display_status(is_live),
        "_sort_dt": dt,
        "_is_live": is_live,
        "_status_raw": status,
    }


def _same_or_near_duplicate(prev: dict, item: dict, minutes: int = 20) -> bool:
    if _dedupe_bucket(prev) != _dedupe_bucket(item):
        return False
    prev_dt = prev.get("_sort_dt")
    item_dt = item.get("_sort_dt")
    if prev_dt and item_dt:
        delta = abs((item_dt - prev_dt).total_seconds()) / 60
        return delta <= minutes
    return True


def _prefer_item(prev: dict, item: dict) -> dict:
    if item["_is_live"] and not prev["_is_live"]:
        return item
    if prev["_is_live"] and not item["_is_live"]:
        return prev

    prev_dt = prev.get("_sort_dt")
    item_dt = item.get("_sort_dt")
    if prev_dt and item_dt:
        return prev if prev_dt <= item_dt else item

    return prev


def _is_same_day_or_live(item: dict) -> bool:
    dt = item.get("_sort_dt")
    if not dt:
        return False
    now = _now_ec()
    return item["_is_live"] or dt.date() == now.date()


def _dedupe_items(items: list[dict]) -> list[dict]:
    out: list[dict] = []
    for item in items:
        merged = False
        for i, prev in enumerate(out):
            if _same_or_near_duplicate(prev, item):
                out[i] = _prefer_item(prev, item)
                merged = True
                break
        if not merged:
            out.append(item)
    return out


def _load_events(path: Path, sport: str) -> list[dict]:
    try:
        if not path.exists():
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            return []
    except Exception:
        return []

    all_items: list[dict] = []
    for row in data:
        if not isinstance(row, dict):
            continue
        item = _normalize_event(row, sport)
        if _is_finished(item["_status_raw"]):
            continue
        all_items.append(item)

    all_items = _dedupe_items(all_items)
    norm = [x for x in all_items if _is_same_day_or_live(x)]
    norm.sort(key=lambda x: (0 if x["_is_live"] else 1, x["_sort_dt"] or datetime.max.replace(tzinfo=EC_TZ)))
    return norm[:10]


def _render_sport(sport: str) -> str:
    title, emoji, picks_cmd = SPORT_HEADERS[sport]
    eventos = _load_events(SPORT_PATHS[sport], sport)
    if not eventos:
        return f"{emoji} {title.upper()} — PROXIMOS PARTIDOS\n\nSin eventos reales cargados para hoy en cache."

    clean = []
    for x in eventos:
        clean.append({
            "datetime": x["datetime"],
            "home": x["home"],
            "away": x["away"],
            "league": x["league"],
            "status": x["status"],
        })
    return format_events_block(title, emoji, clean, picks_cmd)


def handle_eventos_tenis() -> str:
    return _render_sport("tenis")


def handle_eventos_futbol() -> str:
    return _render_sport("futbol")


def handle_eventos_basket() -> str:
    return _render_sport("basket")


if __name__ == "__main__":
    print(handle_eventos_tenis())
    print()
    print(handle_eventos_futbol())
    print()
    print(handle_eventos_basket())
