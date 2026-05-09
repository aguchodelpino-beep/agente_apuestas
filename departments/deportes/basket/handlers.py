from __future__ import annotations
from departments.deportes.basket.service import get_basket_picks

def handle_basket_picks() -> list[dict]:
    return get_basket_picks()

def self_test() -> bool:
    data = handle_basket_picks()
    return isinstance(data, list)

if __name__ == "__main__":
    assert self_test()
    print("SCRIPT OK")
