#!/usr/bin/env python3
from __future__ import annotations

def main() -> int:
    print("MIGRATE_SCHEDULER: desactivado")
    print("La politica oficial usa solo shared/cache_scheduler.py")
    print("No se registran jobs desde scripts/migrate_scheduler.py")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
