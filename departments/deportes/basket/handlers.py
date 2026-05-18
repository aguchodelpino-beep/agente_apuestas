from __future__ import annotations

from departments.deportes.basket.service import build_event_cards
from departments.visuales.formatter import format_events_block


def build_event_cards_handler(limit: int = 50) -> list[dict]:
    return build_event_cards(limit=limit)


def handle_eventos_basket(*args, **kwargs) -> str:
    try:
        cards = build_event_cards(limit=10)
        return format_events_block("Basket", "🏀", cards, action_path="basketpicks")
    except Exception as e:
        return f"🏀 BASKET - PROXIMOS PARTIDOS\n\nError al cargar eventos: {e}"


def handle_basket_picks(*args, **kwargs) -> str:
    try:
        from departments.deportes.basket.analitica_picks_handlers import handle_basket_picks_analitica
        return handle_basket_picks_analitica()
    except Exception as e:
        return f"🏀 BASKET PICKS\n\nError al procesar picks: {e}"


__all__ = ["build_event_cards_handler", "handle_eventos_basket", "handle_basket_picks"]

if __name__ == "__main__":
    print("SCRIPT OK")
