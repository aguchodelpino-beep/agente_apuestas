from __future__ import annotations
from core.config import Config

ODDS_API_KEYS = list(getattr(Config, "ODDS_API_KEYS", []) or [])
RAPIDAPI_KEY = getattr(Config, "RAPIDAPI_KEY", "") or ""
API_SPORTS_KEY = getattr(Config, "API_SPORTS_KEY", "") or ""
FOOTBALL_DATA_KEY = getattr(Config, "FOOTBALL_DATA_KEY", "") or ""
SPORTSGAME_ODDS_KEY = getattr(Config, "SPORTSGAME_ODDS_KEY", "") or ""
ALL_SPORTS_API_KEY = getattr(Config, "ALL_SPORTS_API_KEY", "") or ""
TELEGRAM_TOKEN = getattr(Config, "TELEGRAM_TOKEN", "") or ""

if __name__ == "__main__":
    print("SCRIPT OK")
