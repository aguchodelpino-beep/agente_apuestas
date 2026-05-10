#!/bin/bash
cd /home/aguchodelpino/agente_apuestas

# FIX TENIS handler
cat > departments/deportes/tenis/handlers.py << 'PYEOF'
from telegram.ext import CommandHandler
from departments.deportes.tenis.views import handle_eventos_tenis
from departments.visuales.formatter import format_events_block

def cmd_eventostenis(update, context):
    events = handle_eventos_tenis()
    text = format_events_block("Tenis", "🎾", events, "tenispicks")
    update.message.reply_text(text, parse_mode="Markdown")

handlers = [CommandHandler("eventostenis", cmd_eventostenis)]
PYEOF

# FIX FUTBOL handler  
cat > departments/deportes/futbol/handlers.py << 'PYEOF'
from telegram.ext import CommandHandler
from departments.deportes.futbol.views import handle_eventos_futbol
from departments.visuales.formatter import format_events_block

def cmd_eventosfutbol(update, context):
    events = handle_eventos_futbol()
    text = format_events_block("Fútbol", "⚽", events, "futbolpicks")
    update.message.reply_text(text, parse_mode="Markdown")

handlers = [CommandHandler("eventosfutbol", cmd_eventosfutbol)]
PYEOF

# Reiniciar
sudo systemctl restart telegrambot.service
sleep 2
sudo systemctl status telegrambot.service --no-pager -l
