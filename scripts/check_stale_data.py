from __future__ import annotations

import json
import sys

from core.health import get_health_status


def main() -> int:
    status = get_health_status()
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return 0 if status["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
