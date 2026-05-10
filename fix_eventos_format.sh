#!/bin/bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas

echo "== 1) Reescribiendo formatter =="

cat > departments/visuales/formatter.py << 'PYEOF'
def format_events_block(title: str, emoji: str, events: list, action_path: str = None) -> str:
    if not events:
        return f"{emoji} {title.upper()} — PROXIMOS PARTIDOS\n🗓️ Sin eventos\n━━━━━━━━━━━━━━━━━━━━━━\n\nNo hay eventos disponibles"

    dates = sorted({str(e.get("datetime", "")).split("T")[0] for e in events if e.get("datetime")})
    display_date = dates[0] if dates else "Sin fecha"

    lines = [
        f"{emoji} {title.upper()} — PROXIMOS PARTIDOS",
        f"🗓️ {display_date}",
        "━━━━━━━━━━━━━━━━━━━━━━",
        ""
    ]

    grouped = {}
    for event in events:
        dt = str(event.get("datetime", ""))
        date_str = dt.split("T")[0] if "T" in dt else "Sin fecha"
        grouped.setdefault(date_str, []).append(event)

    for date_str in sorted(grouped.keys()):
        lines.append(f"📅 {date_str}")
        for event in grouped[date_str][:15]:
            dt = str(event.get("datetime", ""))
            time_str = dt.split("T")[1][:5] if "T" in dt else "TBD"
            home = event.get("home") or event.get("player1") or "TBD"
            away = event.get("away") or event.get("player2") or "TBD"
            league = event.get("league") or event.get("tournament") or title
            status = event.get("status") or "Pendiente"
            lines.append(f"   🕐 {time_str} | {home} vs {away} | {league} | {status}")
        lines.append("")

    if action_path:
        lines.append(f"📊 Ver picks → /{action_path}")

    return "\n".join(lines).strip()
PYEOF

echo "== 2) Reescribiendo handler tenis =="

cat > departments/deportes/tenis/handlers.py << 'PYEOF'
from departments.deportes.tenis.views import handle_eventos_tenis
from departments.visuales.formatter import format_events_block

def cmd_eventostenis(message, bot):
    events = handle_eventos_tenis()
    text = format_events_block("Tenis", "🎾", events, "tenispicks")
    bot.reply_to(message, text)
PYEOF

echo "== 3) Reescribiendo handler futbol =="

cat > departments/deportes/futbol/handlers.py << 'PYEOF'
from departments.deportes.futbol.views import handle_eventos_futbol
from departments.visuales.formatter import format_events_block

def cmd_eventosfutbol(message, bot):
    events = handle_eventos_futbol()
    text = format_events_block("Fútbol", "⚽", events, "futbolpicks")
    bot.reply_to(message, text)
PYEOF

echo "== 4) Reiniciando servicio =="
sudo systemctl restart telegrambot.service
sleep 2
sudo systemctl status telegrambot.service --no-pager -l

echo
echo "== 5) Archivos tocados =="
ls -l departments/visuales/formatter.py departments/deportes/tenis/handlers.py departments/deportes/futbol/handlers.py

echo
echo "Listo. Prueba ahora:"
echo "/eventostenis"
echo "/eventosfutbol"
echo "/eventosbasket"
