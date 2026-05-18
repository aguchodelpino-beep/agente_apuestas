from __future__ import annotations

from departments.deportes.futbol.service import build_event_cards
from departments.visuales.formatter import format_events_block


def build_event_cards_handler(limit: int = 50) -> list[dict]:
    return build_event_cards(limit=limit)


def handle_eventos_futbol(*args, **kwargs) -> str:
    try:
        cards = build_event_cards(limit=10)
        normalized = []
        for item in cards:
            normalized.append({
                "datetime": item.get("start", ""),
                "home": (item.get("title", "TBD vs TBD").split(" vs ", 1)[0] if " vs " in item.get("title", "") else item.get("title", "TBD")),
                "away": (item.get("title", "TBD vs TBD").split(" vs ", 1)[1] if " vs " in item.get("title", "") else "TBD"),
                "league": item.get("tour", "Fútbol"),
                "status": item.get("status", "scheduled"),
            })
        return format_events_block("Fútbol", "⚽", normalized, action_path="futbolpicks")
    except Exception as e:
        return f"⚽ FUTBOL - PROXIMOS PARTIDOS\n\nError al cargar eventos: {e}"


def handle_futbol_picks(*args, **kwargs) -> str:
    try:
        from departments.deportes.futbol.analitica_picks_handlers import handle_futbol_picks_analitica
        return handle_futbol_picks_analitica()
    except Exception as e:
        return f"⚽ FUTBOL PICKS\n\nError al procesar picks: {e}"


__all__ = ["build_event_cards_handler", "handle_eventos_futbol", "handle_futbol_picks"]

if __name__ == "__main__":
    print("SCRIPT OK")
