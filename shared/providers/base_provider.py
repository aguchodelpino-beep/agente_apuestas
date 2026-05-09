from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseProvider(ABC):
    sport: str

    @abstractmethod
    async def fetch(self) -> list[dict[str, Any]]:
        raise NotImplementedError
