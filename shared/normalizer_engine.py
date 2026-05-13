from __future__ import annotations

import hashlib
import re
import unicodedata
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


TEAM_ALIASES = {
    "man utd": "Manchester United",
    "manchester utd": "Manchester United",
    "manchester united": "Manchester United",
    "barca": "Barcelona",
    "fc barcelona": "Barcelona",
    "barcelona": "Barcelona",
    "la lakers": "Los Angeles Lakers",
    "los angeles lakers": "Los Angeles Lakers",
    "lakers": "Los Angeles Lakers",
}

LEAGUE_ALIASES = {
    "epl": "Premier League",
    "premier league": "Premier League",
    "la liga": "La Liga",
    "laliga": "La Liga",
    "nba": "NBA",
    "atp": "ATP",
    "wta": "WTA",
}

TBD_VALUES = {"tbd", "tba", "unknown", "n/a", "-", ""}


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def canonical_key(value: str) -> str:
    value = strip_accents(value).lower().strip()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def normalize_team_name(name: str) -> str:
    raw = (name or "").strip()
    key = canonical_key(raw)
    if key in TBD_VALUES or not key:
        return "TBD"
    return TEAM_ALIASES.get(key, raw.strip())


def normalize_league_name(name: str) -> str:
    raw = (name or "").strip()
    key = canonical_key(raw)
    if not key:
        return "Unknown League"
    return LEAGUE_ALIASES.get(key, raw.strip())


def normalize_sport_name(name: str) -> str:
    key = canonical_key(name)
    mapping = {
        "soccer": "futbol",
        "football": "futbol",
        "futbol": "futbol",
        "tennis": "tenis",
        "tenis": "tenis",
        "basketball": "basket",
        "nba": "basket",
        "basket": "basket",
    }
    return mapping.get(key, key or "unknown")


def normalize_start_time(value: str | None, source_tz: str = "UTC") -> str | None:
    if not value:
        return None

    text = value.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        try:
            dt = datetime.strptime(value.strip(), "%Y-%m-%d %H:%M:%S")
            dt = dt.replace(tzinfo=ZoneInfo(source_tz))
        except ValueError:
            return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(source_tz))

    return (
        dt.astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def slugify(value: str) -> str:
    key = canonical_key(value)
    return key.replace(" ", "-")


def build_internal_event_id(
    *,
    sport: str,
    league: str,
    home_team: str,
    away_team: str,
    start_time: str | None,
) -> str:
    normalized_start = normalize_start_time(start_time) if start_time else None
    safe_start = normalized_start or "unknown-start"

    normalized = "|".join(
        [
            normalize_sport_name(sport),
            slugify(normalize_league_name(league)),
            slugify(normalize_team_name(home_team)),
            slugify(normalize_team_name(away_team)),
            safe_start,
        ]
    )
    digest = hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:16]
    return f"evt_{digest}"


def _extract_teams_from_title(title: str) -> tuple[str, str]:
    if not title:
        return "TBD", "TBD"

    separators = [" vs ", " VS ", " v ", " - ", " @ "]
    for sep in separators:
        if sep in title:
            left, right = title.split(sep, 1)
            return normalize_team_name(left), normalize_team_name(right)

    return normalize_team_name(title), "TBD"


def normalize_event_payload(payload: dict, *, source_tz: str = "UTC") -> dict:
    title = (payload.get("title") or payload.get("match") or "").strip()

    home = payload.get("home_team") or payload.get("home") or payload.get("team1") or ""
    away = payload.get("away_team") or payload.get("away") or payload.get("team2") or ""

    if not home and not away and title:
        home, away = _extract_teams_from_title(title)

    home = normalize_team_name(home)
    away = normalize_team_name(away)

    league = normalize_league_name(
        payload.get("league")
        or payload.get("competition")
        or payload.get("sport_title")
        or ""
    )

    sport = normalize_sport_name(
        payload.get("sport")
        or payload.get("sport_title")
        or payload.get("sport_key")
        or ""
    )

    start_time = normalize_start_time(
        payload.get("start_time")
        or payload.get("commence_time")
        or payload.get("date")
        or payload.get("datetime"),
        source_tz=source_tz,
    )

    return {
        "sport": sport,
        "league": league,
        "start_time": start_time,
        "home_team": home,
        "away_team": away,
        "teams": [home, away],
        "internal_event_id": build_internal_event_id(
            sport=sport,
            league=league,
            home_team=home,
            away_team=away,
            start_time=start_time,
        ),
    }


def is_valid_normalized_event(normalized: dict) -> bool:
    return bool(
        normalized.get("start_time")
        and normalized.get("home_team") not in {"", "TBD"}
        and normalized.get("away_team") not in {"", "TBD"}
    )

if __name__ == "__main__":
    print("SCRIPT OK")
