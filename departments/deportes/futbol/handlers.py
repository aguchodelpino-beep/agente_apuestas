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
def cmd_eventosfutbol(message):
    from departments.visuales.formatter import format_events_block
    events = handle_eventos_futbol()
    text = format_events_block("Fútbol", "⚽", events, "futbolpicks")
    bot.reply_to(message, text, parse_mode="Markdown")
