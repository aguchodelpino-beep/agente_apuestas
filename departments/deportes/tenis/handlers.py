from __future__ import annotations

from departments.deportes.tenis.service import build_event_cards
from departments.visuales.formatter import render_eventos_tenis, render_tenis_picks


def handle_eventos_tenis(limit: int = 10) -> str:
    cards = build_event_cards(limit=limit)
    return render_eventos_tenis(cards)


def handle_tenis_picks(limit: int = 10) -> str:
    return render_tenis_picks()
