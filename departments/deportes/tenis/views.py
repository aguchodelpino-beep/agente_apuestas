from __future__ import annotations

from departments.deportes.tenis.service import get_fixtures, get_live, get_one
from departments.deportes.tenis.analitica_picks_handlers import handle_tenis_picks_analitica


def tenis_index():
    return get_fixtures()


def tenis_live():
    return get_live()


def tenis_detail(fixture_id: str):
    return get_one(fixture_id)


def handle_eventos_tenis(*args, **kwargs):
    data = get_fixtures()
    try:
        from departments.visuales.formatter import format_tenis_message
        return format_tenis_message(data)
    except Exception:
        return data


def handle_tenis_picks(*args, **kwargs):
    # 1. usa el flujo analítico con Kelly + registro histórico
    try:
        return handle_tenis_picks_analitica()
    except Exception:
        # 2. fallback a mensaje genérico
        return "🎾 TENIS PICKS\n\nSin picks disponibles en la capa analitica."

if __name__ == "__main__":
    print("SCRIPT OK")
