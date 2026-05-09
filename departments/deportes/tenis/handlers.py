from __future__ import annotations

from departments.deportes.tenis.service import build_event_cards, build_event_groups

try:
    from departments.visuales.formatter import render_eventos_tenis, render_tenis_picks
except ImportError:
    from departments.visuales.formatter import rendereventostenis as render_eventos_tenis
    from departments.visuales.formatter import rendertenispicks as render_tenis_picks


def handle_eventos_tenis(limit: int = 10) -> str:
    cards = build_event_cards(limit=limit)
    return render_eventos_tenis(cards)


def handle_tenis_picks(limit: int = 10) -> str:
    return render_tenis_picks()


# Aliases legacy
handleeventostenis = handle_eventos_tenis
handletenispicks = handle_tenis_picks
buildeventcards = build_event_cards
buildeventgroups = build_event_groups
