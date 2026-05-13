from __future__ import annotations

from departments.analitica.deportes.basket.service import build_basket_pick_messages


def handle_basket_picks_analitica(*args, **kwargs) -> str:
    lines = build_basket_pick_messages(bankroll=1000.0)
    return "\n".join(lines)

if __name__ == "__main__":
    print("SCRIPT OK")
