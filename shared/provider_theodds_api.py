from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(".env").resolve(), override=False)

BASE = "https://api.the-odds-api.com/v4"
STATE_PATHS = [
    Path("cachediario/odds_api_state.json"),
    Path("cache_diario/odds_api_state.json"),
]
RATE_LIMIT_SECONDS = 60 * 30
UNAUTHORIZED_SECONDS = 60 * 60 * 6
REQUEST_ERROR_SECONDS = 60


def _first_nonempty(*values: str | None) -> str:
    for v in values:
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def _parse_key_list(raw: str) -> list[str]:
    text = raw.strip()
    if not text:
        return []
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [str(k).strip() for k in parsed if str(k).strip()]
    except Exception:
        pass
    return [k.strip().strip('"').strip("'") for k in text.replace("\n", ",").split(",") if k.strip().strip('"').strip("'")]


def _load_state() -> dict[str, Any]:
    for path in STATE_PATHS:
        if path.exists():
            try:
                data = json.loads(path.read_text())
                if isinstance(data, dict):
                    data.setdefault("keys", {})
                    data.setdefault("last_good", "")
                    data.setdefault("last_index", 0)
                    return data
            except Exception:
                pass
    return {"keys": {}, "last_good": "", "last_index": 0}


def _save_state(state: dict[str, Any]) -> None:
    for path in STATE_PATHS:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(state, indent=2, ensure_ascii=False))
        except Exception:
            pass


def _config_key() -> str:
    try:
        from config import Config
        key = (Config.get_odds_key() or "").strip()
        if key:
            return key
    except Exception:
        pass
    return ""


def _all_keys() -> list[str]:
    keys: list[str] = []

    config_key = _config_key()
    if config_key:
        keys.append(config_key)

    multi = _first_nonempty(
        os.getenv("ODDS_API_KEYS"),
        os.getenv("ODDSAPI_KEYS"),
        os.getenv("ODDSAPIKEYS"),
    )
    if multi:
        keys.extend(_parse_key_list(multi))

    single = _first_nonempty(
        os.getenv("ODDS_API_KEY"),
        os.getenv("SPORTS_API_KEY"),
    )
    if single:
        keys.append(single)

    unique: list[str] = []
    seen: set[str] = set()
    for k in keys:
        if k not in seen:
            seen.add(k)
            unique.append(k)

    if not unique:
        raise RuntimeError("No existe key válida de Odds API en config.py/.env")

    return unique


def _candidate_keys() -> list[str]:
    keys = _all_keys()
    state = _load_state()
    meta = state.get("keys", {})
    now = int(time.time())

    ready: list[str] = []
    delayed: list[str] = []

    for k in keys:
        item = meta.get(k, {})
        disabled_until = int(item.get("disabled_until", 0) or 0)
        if disabled_until > now:
            delayed.append(k)
        else:
            ready.append(k)

    ordered = ready + delayed

    last_good = state.get("last_good", "")
    if last_good in ordered:
        idx = ordered.index(last_good)
        ordered = ordered[idx:] + ordered[:idx]

    return ordered


def _mask(key: str) -> str:
    if len(key) <= 8:
        return key
    return f"{key[:6]}...{key[-4:]}"


def _mark_key(key: str, status: str, cooldown: int = 0, error: str = "") -> None:
    state = _load_state()
    state.setdefault("keys", {})
    item = state["keys"].setdefault(key, {})
    item["status"] = status
    item["last_error"] = error[:500]
    item["updated_at"] = int(time.time())
    item["disabled_until"] = int(time.time()) + cooldown if cooldown > 0 else 0
    _save_state(state)


def _mark_success(key: str) -> None:
    state = _load_state()
    state.setdefault("keys", {})
    item = state["keys"].setdefault(key, {})
    item["status"] = "ok"
    item["last_error"] = ""
    item["updated_at"] = int(time.time())
    item["disabled_until"] = 0
    state["last_good"] = key
    try:
        state["last_index"] = _all_keys().index(key)
    except Exception:
        pass
    _save_state(state)


def _get(path: str, params: dict[str, Any] | None = None) -> Any:
    p = dict(params or {})
    errors: list[str] = []

    for key in _candidate_keys():
        req_params = dict(p)
        req_params["apiKey"] = key

        try:
            r = requests.get(f"{BASE}{path}", params=req_params, timeout=40)

            if r.status_code in (401, 403):
                _mark_key(
                    key,
                    "unauthorized",
                    cooldown=UNAUTHORIZED_SECONDS,
                    error=f"{r.status_code}: {r.text}",
                )
                errors.append(f"{_mask(key)} -> {r.status_code}")
                continue

            if r.status_code == 429:
                _mark_key(
                    key,
                    "rate_limited",
                    cooldown=RATE_LIMIT_SECONDS,
                    error=f"{r.status_code}: {r.text}",
                )
                errors.append(f"{_mask(key)} -> 429")
                continue

            r.raise_for_status()
            _mark_success(key)
            return r.json()

        except requests.RequestException as e:
            _mark_key(key, "error", cooldown=REQUEST_ERROR_SECONDS, error=str(e))
            errors.append(f"{_mask(key)} -> {e.__class__.__name__}")
            continue

    raise RuntimeError("Odds API sin keys disponibles: " + " | ".join(errors))


def get_sports() -> list[dict[str, Any]]:
    data = _get("/sports")
    return data if isinstance(data, list) else []


def get_odds(
    sport_key: str,
    regions: str = "us,eu",
    markets: str = "h2h,spreads,totals",
    odds_format: str = "decimal",
    date_format: str = "iso",
) -> list[dict[str, Any]]:
    data = _get(
        f"/sports/{sport_key}/odds",
        {
            "regions": regions,
            "markets": markets,
            "oddsFormat": odds_format,
            "dateFormat": date_format,
        },
    )
    return data if isinstance(data, list) else []


def get_active_tennis_keys() -> list[str]:
    keys: list[str] = []
    for row in get_sports():
        key = row.get("key")
        group = row.get("group")
        active = row.get("active", True)
        if not isinstance(key, str):
            continue
        if active and (key.startswith("tennis_") or group == "Tennis"):
            keys.append(key)
    return sorted(set(keys))

if __name__ == "__main__":
    print("SCRIPT OK")
