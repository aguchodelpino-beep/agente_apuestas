from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from shared.cache import CacheManager, today_str

class FixtureRepository(ABC):
    @abstractmethod
    def list_fixtures(self, day: str | None = None) -> list[dict[str, Any]]:
        raise NotImplementedError

class JsonCacheRepository(FixtureRepository):
    def __init__(self, sport: str, cache: CacheManager | None = None):
        self.sport = sport
        self.cache = cache or CacheManager()

    def list_fixtures(self, day: str | None = None) -> list[dict[str, Any]]:
        data = self.cache.read_day(self.sport, day or today_str())
        return data.get("payload", [])

    def get_snapshot_meta(self, day: str | None = None) -> dict[str, Any]:
        data = self.cache.read_day(self.sport, day or today_str())
        return {
            "sport": data.get("sport", self.sport),
            "date": data.get("date"),
            "generated_at": data.get("generated_at"),
            "source": data.get("source"),
            "records_count": data.get("records_count", len(data.get("payload", []))),
            "payload_hash": data.get("payload_hash"),
        }
