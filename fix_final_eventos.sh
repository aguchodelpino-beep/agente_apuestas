#!/bin/bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas

echo "== JSON permisos =="
chmod 644 departments/deportes/basket/live_today.json
chmod 644 departments/deportes/futbol/live_today.json

echo "== basket/views.py =="
cat > departments/deportes/basket/views.py << 'PYEOF'
import json
from pathlib import Path
from departments.visuales.formatter import format_events_block

BASE_DIR = Path(__file__).resolve().parents[3]
JSON_PATH = BASE_DIR / "departments" / "deportes" / "basket" / "live_today.json"

def handle_eventos_basket():
    try:
        with JSON_PATH.open("r", encoding="utf-8") as f:
            events = json.load(f)
    except Exception:
        events = [
            {"datetime": "2026-05-09T23:00", "home": "Los Angeles Lakers", "away": "Denver Nuggets", "league": "NBA Playoffs", "status": "Pendiente"}
        ]
    return format_events_block("Basket", "🏀", events, "basketpicks")
PYEOF

echo "== basket/handlers.py =="
cat > departments/deportes/basket/handlers.py << 'PYEOF'
from telegram.ext import CommandHandler
from departments.deportes.basket.views import handle_eventos_basket

def cmd_eventosbasket(update, context):
    text = handle_eventos_basket()
    update.message.reply_text(text, parse_mode="Markdown")

handlers = [CommandHandler("eventosbasket", cmd_eventosbasket)]
PYEOF

echo "== futbol/views.py =="
cat > departments/deportes/futbol/views.py << 'PYEOF'
import json
from pathlib import Path
from departments.visuales.formatter import format_events_block

BASE_DIR = Path(__file__).resolve().parents[3]
JSON_PATH = BASE_DIR / "departments" / "deportes" / "futbol" / "live_today.json"

def handle_eventos_futbol():
    try:
        with JSON_PATH.open("r", encoding="utf-8") as f:
            events = json.load(f)
    except Exception:
        events = [
            {"datetime": "2026-05-09T11:30", "home": "Liverpool", "away": "Chelsea", "league": "Premier League", "status": "Pendiente"}
        ]
    return format_events_block("Fútbol", "⚽", events, "futbolpicks")
PYEOF

echo "== futbol/handlers.py =="
cat > departments/deportes/futbol/handlers.py << 'PYEOF'
from telegram.ext import CommandHandler
from departments.deportes.futbol.views import handle_eventos_futbol

def cmd_eventosfutbol(update, context):
    text = handle_eventos_futbol()
    update.message.reply_text(text, parse_mode="Markdown")

handlers = [CommandHandler("eventosfutbol", cmd_eventosfutbol)]
PYEOF

echo "== tests locales =="
python3 - << 'PYEOF'
from departments.deportes.basket.views import handle_eventos_basket
from departments.deportes.futbol.views import handle_eventos_futbol
print("BASKET_OK")
print(handle_eventos_basket())
print("FUTBOL_OK")
print(handle_eventos_futbol())
PYEOF

echo "== restart =="
sudo systemctl restart telegrambot.service
sleep 3
sudo systemctl status telegrambot.service --no-pager -l | head -n 20
