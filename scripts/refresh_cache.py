from __future__ import annotations

from core.logging import get_logger
from scheduler import refresh_all

logger = get_logger(__name__)


def main() -> int:
    fetchers = {}
    result = refresh_all(fetchers)
    logger.info("refresh_result=%s", result)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
