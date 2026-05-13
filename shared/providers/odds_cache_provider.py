from __future__ import annotations

from typing import Any

from core.logging import get_logger
from shared.cache import load_sport_day, save_sport_day
from shared.datetime_utils import today_str

logger = get_logger(__name__)


class OddsCacheProvider:
    def __init__(self, sport: str) -> None:
        self.sport = sport.lower().strip()

    def load_today(self) -> list[dict[str, Any]]:
        return load_sport_day(self.sport, today_str())

    def save_today(self, items: list[dict[str, Any]]) -> None:
        save_sport_day(self.sport, today_str(), items)

    def has_today(self) -> bool:
        return len(self.load_today()) > 0

    def refresh_with(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        self.save_today(items)
        logger.info("provider_refresh sport=%s items=%s", self.sport, len(items))
        return items

if __name__ == "__main__":
    print("SCRIPT OK")
