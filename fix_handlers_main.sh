#!/bin/bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas

cp handlers.py handlers.py.bak.$(date +%s)

cat > handlers.py << 'PYEOF'
from departments.visuales.formatter import render_eventos_basket, format_events_block

def handle_eventos_tenis() -> str:
    eventos = [
        {"datetime": "2026-05-09T14:00", "home": "Flavio Cobolli", "away": "Terence Atmane", "league": "ATP Roma", "status": "Pendiente"},
        {"datetime": "2026-05-09T14:07", "home": "Aryna Sabalenka", "away": "Sorana Cirstea", "league": "WTA Roma", "status": "Pendiente"},
        {"datetime": "2026-05-09T15:15", "home": "Nikoloz Basilashvili", "away": "Ben Shelton", "league": "ATP Roma", "status": "Pendiente"},
        {"datetime": "2026-05-09T16:00", "home": "Frances Tiafoe", "away": "Ignacio Buse", "league": "ATP Roma", "status": "Pendiente"},
        {"datetime": "2026-05-09T16:30", "home": "Hamad Medjedovic", "away": "Joao Fonseca", "league": "ATP Roma", "status": "Pendiente"},
        {"datetime": "2026-05-09T16:30", "home": "Viktorija Golubic", "away": "Mirra Andreeva", "league": "WTA Roma", "status": "Pendiente"},
        {"datetime": "2026-05-09T17:00", "home": "Jannik Sinner", "away": "Sebastian Ofner", "league": "ATP Roma", "status": "Pendiente"},
        {"datetime": "2026-05-09T17:30", "home": "Taylor Townsend", "away": "Iva Jović", "league": "WTA Roma", "status": "Pendiente"},
        {"datetime": "2026-05-09T17:40", "home": "Alexei Popyrin", "away": "Jakub Mensik", "league": "ATP Roma", "status": "Pendiente"},
        {"datetime": "2026-05-09T17:40", "home": "Andrea Pellegrino", "away": "Arthur Fils", "league": "ATP Roma", "status": "Pendiente"},
    ]
    return format_events_block("Tenis", "🎾", eventos, "tenispicks")


def handle_eventos_futbol() -> str:
    eventos = [
        {"datetime": "2026-05-09T14:25", "home": "TBD", "away": "TBD", "league": "Fútbol", "status": "Pendiente"},
        {"datetime": "2026-05-09T16:00", "home": "TBD", "away": "TBD", "league": "Fútbol", "status": "Pendiente"},
        {"datetime": "2026-05-09T16:30", "home": "TBD", "away": "TBD", "league": "Fútbol", "status": "Pendiente"},
        {"datetime": "2026-05-09T16:30", "home": "TBD", "away": "TBD", "league": "Fútbol", "status": "Pendiente"},
        {"datetime": "2026-05-09T16:30", "home": "TBD", "away": "TBD", "league": "Fútbol", "status": "Pendiente"},
        {"datetime": "2026-05-09T17:00", "home": "TBD", "away": "TBD", "league": "Fútbol", "status": "Pendiente"},
        {"datetime": "2026-05-09T18:30", "home": "TBD", "away": "TBD", "league": "Fútbol", "status": "Pendiente"},
        {"datetime": "2026-05-09T18:45", "home": "TBD", "away": "TBD", "league": "Fútbol", "status": "Pendiente"},
        {"datetime": "2026-05-09T19:00", "home": "TBD", "away": "TBD", "league": "Fútbol", "status": "Pendiente"},
        {"datetime": "2026-05-09T20:30", "home": "TBD", "away": "TBD", "league": "Fútbol", "status": "Pendiente"},
        {"datetime": "2026-05-09T23:30", "home": "TBD", "away": "TBD", "league": "Fútbol", "status": "Pendiente"},
        {"datetime": "2026-05-09T23:30", "home": "TBD", "away": "TBD", "league": "Fútbol", "status": "Pendiente"},
        {"datetime": "2026-05-09T23:30", "home": "TBD", "away": "TBD", "league": "Fútbol", "status": "Pendiente"},
        {"datetime": "2026-05-10T00:30", "home": "TBD", "away": "TBD", "league": "Fútbol", "status": "Pendiente"},
        {"datetime": "2026-05-10T01:15", "home": "TBD", "away": "TBD", "league": "Fútbol", "status": "Pendiente"},
    ]
    return format_events_block("Fútbol", "⚽", eventos, "futbolpicks")


def handle_eventos_basket() -> str:
    cards = [
        {"datetime": "2026-05-09T17:00", "home": "TBD", "away": "TBD", "league": "Basket", "status": "scheduled"},
        {"datetime": "2026-05-09T19:10", "home": "TBD", "away": "TBD", "league": "Basket", "status": "scheduled"},
        {"datetime": "2026-05-09T19:30", "home": "TBD", "away": "TBD", "league": "Basket", "status": "scheduled"},
        {"datetime": "2026-05-10T00:00", "home": "TBD", "away": "TBD", "league": "Basket", "status": "scheduled"},
        {"datetime": "2026-05-10T00:40", "home": "TBD", "away": "TBD", "league": "Basket", "status": "scheduled"},
        {"datetime": "2026-05-10T01:00", "home": "TBD", "away": "TBD", "league": "Basket", "status": "scheduled"},
        {"datetime": "2026-05-10T17:00", "home": "TBD", "away": "TBD", "league": "Basket", "status": "scheduled"},
        {"datetime": "2026-05-10T19:00", "home": "TBD", "away": "TBD", "league": "Basket", "status": "scheduled"},
        {"datetime": "2026-05-10T19:40", "home": "TBD", "away": "TBD", "league": "Basket", "status": "scheduled"},
        {"datetime": "2026-05-10T23:40", "home": "TBD", "away": "TBD", "league": "Basket", "status": "scheduled"},
    ]
    return render_eventos_basket(cards)


if __name__ == "__main__":
    print(handle_eventos_tenis())
    print()
    print(handle_eventos_futbol())
    print()
    print(handle_eventos_basket())
PYEOF

sudo systemctl restart telegrambot.service
sleep 2
sudo systemctl status telegrambot.service --no-pager -l

echo
echo "=== PRUEBA RAPIDA ==="
python handlers.py | head -n 80
