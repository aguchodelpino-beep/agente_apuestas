from __future__ import annotations

from shared.picks_cache import render_picks
from departments.visuales.formatter import render_eventos_basket
from departments.deportes.tenis.service import build_event_cards as tenis_cards

try:
    from departments.deportes.futbol.service import build_event_cards as futbol_cards
except Exception:
    futbol_cards = None

try:
    from departments.deportes.basket.service import build_event_cards as basket_cards
except Exception:
    basket_cards = None


def handle_eventos_tenis() -> str:
    cards = tenis_cards(10)
    if not cards:
        return "🎾 Sin eventos tenis hoy"

    lines = ["🎾 *EVENTOS TENIS HOY*"]
    for card in cards:
        title = card.get("title") or f"{card.get('home', '?')} vs {card.get('away', '?')}"
        start = card.get("start") or ""
        markets = card.get("bookmakers", card.get("markets", 0))
        line = f"- {title}"
        if start:
            line += f" _{start[:16]}_"
        if markets not in ("", None):
            line += f" ({markets})"
        lines.append(line)
    return "\n".join(lines)


def handle_eventos_futbol() -> str:
    if futbol_cards is None:
        return "⚽ Fútbol temporalmente en mantenimiento"
    cards = futbol_cards(15)
    if not cards:
        return "⚽ Sin eventos fútbol hoy"

    lines = ["⚽ *EVENTOS FÚTBOL HOY*"]
    for card in cards:
        home = card.get("home", "?")
        away = card.get("away", "?")
        start = card.get("start", "")
        books = card.get("bookmakers", card.get("markets", 0))
        idx = card.get("index", "-")
        line = f"*{idx}* {home} vs {away}"
        if start:
            line += f" _{start[:16]}_"
        line += f" ({books})"
        lines.append(line)
    return "\n".join(lines)


def handle_eventos_basket() -> str:
    if basket_cards is None:
        return "🏀 Basket temporalmente en mantenimiento"
    cards = basket_cards(10)
    return render_eventos_basket(cards)


def handle_picks_futbol() -> str:
    return render_picks("futbol")


def handle_picks_basket() -> str:
    return render_picks("basket")


if __name__ == "__main__":
    print("TENIS:")
    print(handle_eventos_tenis())
    print("\nFUTBOL:")
    print(handle_eventos_futbol())
    print("\nBASKET:")
    print(handle_eventos_basket())
