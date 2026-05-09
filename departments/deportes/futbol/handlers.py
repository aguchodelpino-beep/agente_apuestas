from __future__ import annotations
from departments.deportes.futbol.service import get_futbol_picks

def handle_futbol_picks() -> list[dict]:
    return get_futbol_picks()

def self_test() -> bool:
    data = handle_futbol_picks()
    return isinstance(data, list)

if __name__ == "__main__":
    assert self_test()
    print("SCRIPT OK")
