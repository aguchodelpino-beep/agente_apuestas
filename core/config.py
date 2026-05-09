from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _to_int(value: str | None, default: int) -> int:
    try:
        return int(value) if value is not None else default
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_env: str
    debug: bool
    timezone: str

    base_dir: Path
    data_dir: Path
    raw_dir: Path
    cache_dir: Path
    logs_dir: Path

    rapidapi_key: str
    telegram_bot_token: str
    telegram_chat_id: str

    morning_refresh_hour: int
    noon_refresh_hour: int
    evening_refresh_hour: int

    request_timeout: int
    max_retries: int


def load_settings() -> Settings:
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"
    raw_dir = data_dir / "raw"
    cache_dir = data_dir / "cache"
    logs_dir = base_dir / "logs"

    raw_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    return Settings(
        app_name=os.getenv("APP_NAME", "agente_apuestas"),
        app_env=os.getenv("APP_ENV", "development"),
        debug=_to_bool(os.getenv("DEBUG"), False),
        timezone=os.getenv("APP_TIMEZONE", "America/Guayaquil"),

        base_dir=base_dir,
        data_dir=data_dir,
        raw_dir=raw_dir,
        cache_dir=cache_dir,
        logs_dir=logs_dir,

        rapidapi_key=os.getenv("RAPIDAPI_KEY", ""),
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),

        morning_refresh_hour=_to_int(os.getenv("MORNING_REFRESH_HOUR"), 3),
        noon_refresh_hour=_to_int(os.getenv("NOON_REFRESH_HOUR"), 12),
        evening_refresh_hour=_to_int(os.getenv("EVENING_REFRESH_HOUR"), 18),

        request_timeout=_to_int(os.getenv("REQUEST_TIMEOUT"), 25),
        max_retries=_to_int(os.getenv("MAX_RETRIES"), 3),
    )


settings = load_settings()
