#!/bin/bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas

cp departments/visuales/formatter.py departments/visuales/formatter.py.before_restore_$(date +%s) || true

cat > departments/visuales/formatter.py << 'PYEOF'
def render_eventos_basket(cards):
    lines = [
        "🏀 BASKET — PROXIMOS PARTIDOS",
        "🗓️ 09/05/2026",
        "━━━━━━━━━━━━━━━━━━━━━━",
        ""
    ]

    grouped = {}
    for card in cards or []:
        dt = str(card.get("datetime", ""))
        date_str = dt.split("T")[0] if "T" in dt else "Sin fecha"
        grouped.setdefault(date_str, []).append(card)

    for date_str in sorted(grouped.keys()):
        lines.append(f"📅 {date_str}")
        for card in grouped[date_str]:
            dt = str(card.get("datetime", ""))
            time_str = dt.split("T")[1][:5] if "T" in dt else "TBD"
            home = card.get("home") or "TBD"
            away = card.get("away") or "TBD"
            league = card.get("league") or "Basket"
            status = card.get("status") or "Pendiente"
            lines.append(f"   🕐 {time_str} | {home} vs {away} | {league} | {status}")
        lines.append("")

    lines.append("📊 Ver picks → /basketpicks")
    return "\n".join(lines).strip()


def format_events_block(title: str, emoji: str, events: list, action_path: str = None) -> str:
    if not events:
        return f"{emoji} {title.upper()} — PROXIMOS PARTIDOS\n🗓️ Sin eventos\n━━━━━━━━━━━━━━━━━━━━━━\n\nNo hay eventos disponibles"

    dates = sorted({str(e.get('datetime', '')).split('T')[0] for e in events if e.get('datetime')})
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
            home = event.get("home") or event.get("player1") or event.get("team1") or "TBD"
            away = event.get("away") or event.get("player2") or event.get("team2") or "TBD"
            league = event.get("league") or event.get("tournament") or title
            status = event.get("status") or "Pendiente"
            lines.append(f"   🕐 {time_str} | {home} vs {away} | {league} | {status}")
        lines.append("")

    if action_path:
        lines.append(f"📊 Ver picks → /{action_path}")

    return "\n".join(lines).strip()
PYEOF

sudo systemctl restart telegrambot.service
sleep 3

echo "=== STATUS ==="
sudo systemctl status telegrambot.service --no-pager -l

echo
echo "=== IMPORT CHECK ==="
python - << 'PYEOF'
from departments.visuales.formatter import render_eventos_basket, format_events_block
print("OK_IMPORTS")
PYEOF

echo
echo "=== LISTO ==="
echo "Prueba ahora:"
echo "/eventosbasket"
echo "/eventostenis"
echo "/eventosfutbol"
