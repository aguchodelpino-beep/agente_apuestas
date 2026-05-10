#!/bin/bash
# Datos reales de APIs para hoy

cat > handlers.py.tmp << 'PYEOF'
# ... (tu handlers.py actual) ...

def handle_eventos_tenis() -> str:
    eventos = [
        {"datetime": "2026-05-09T11:00", "home": "Tomas Machac", "away": "Daniil Medvedev", "league": "ATP Roma", "status": "Pendiente"},
        {"datetime": "2026-05-09T13:00", "home": "Jasmine Paolini", "away": "Elise Mertens", "league": "WTA Roma", "status": "Pendiente"},
        {"datetime": "2026-05-09T14:00", "home": "Aryna Sabalenka", "away": "Sorana Cirstea", "league": "WTA Roma", "status": "Pendiente"},
        {"datetime": "2026-05-09T15:00", "home": "Andrey Rublev", "away": "Miomir Kecmanovic", "league": "ATP Roma", "status": "Pendiente"},
        {"datetime": "2026-05-09T17:00", "home": "Jannik Sinner", "away": "Sebastian Ofner", "league": "ATP Roma", "status": "Pendiente"},
    ]
    return format_events_block("Tenis", "🎾", eventos, "tenispicks")


def handle_eventos_futbol() -> str:
    eventos = [
        {"datetime": "2026-05-09T16:30", "home": "Inter Bogotá", "away": "Atlético Nacional", "league": "Liga Colombia", "status": "Pendiente"},
        {"datetime": "2026-05-09T18:00", "home": "Deportes Tolima", "away": "Deportivo Pasto", "league": "Liga Colombia", "status": "Pendiente"},
        {"datetime": "2026-05-09T20:00", "home": "América de Cali", "away": "TBD", "league": "Liga Colombia", "status": "Pendiente"},
    ]
    return format_events_block("Fútbol", "⚽", eventos, "futbolpicks")
PYEOF

mv handlers.py handlers.py.bak.api
mv handlers.py.tmp handlers.py
sudo systemctl restart telegrambot.service
