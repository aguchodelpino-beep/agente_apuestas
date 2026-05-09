from __future__ import annotations

from collections import OrderedDict
from datetime import datetime
from typing import Any
from shared.datetimeutils import daylabel, hourlabel

from shared.datetime_utils import day_label, hour_label

MONTHS = {
    1: "01", 2: "02", 3: "03", 4: "04", 5: "05", 6: "06",
    7: "07", 8: "08", 9: "09", 10: "10", 11: "11", 12: "12",
}


def _today_ec() -> str:
    now = datetime.now()
    return f"{now.day:02d}/{MONTHS[now.month]}/{now.year}"


def _title_case_league(name: str) -> str:
    if not name:
        return "Liga"
    name = name.replace("_", " ").strip()
    return " ".join(x.capitalize() for x in name.split())


def _is_live(card: dict[str, Any]) -> bool:
    status = str(card.get("status", "")).lower()
    return status in {"live", "inplay", "in_play", "ongoing"}


def render_eventos_basket(cards: list[dict[str, Any]]) -> str:
    if not cards:
        return "🏀 *BASKET — PROXIMOS PARTIDOS*\n🗓️ " + _today_ec() + "\n━━━━━━━━━━━━━━━━━━━━━━\n\nSin eventos en cache.\n\n📊 Ver picks → /basketpicks"

    grouped: OrderedDict[str, list[dict[str, Any]]] = OrderedDict()
    for card in cards:
        start = card.get("start") or ""
        day = day_label(start) if start else "Sin fecha"
        grouped.setdefault(day, []).append(card)

    lines = [
        "🏀 *BASKET — PROXIMOS PARTIDOS*",
        f"🗓️ {_today_ec()}",
        "━━━━━━━━━━━━━━━━━━━━━━",
    ]

    for day, items in grouped.items():
        lines.append("")
        lines.append(f"📅 {day}")
        for card in items:
            home = card.get("home", "TBD")
            away = card.get("away", "TBD")
            league = _title_case_league(card.get("league") or card.get("sport_key") or "Basket")
            if _is_live(card):
                lines.append(f"   🔴 EN VIVO | {home} vs {away} | {league}")
            else:
                hour = hour_label(card.get("start") or "") if card.get("start") else "--:--"
                lines.append(f"   🕐 {hour} | {home} vs {away} | {league}")

    lines.append("")
    lines.append("📊 Ver picks → /basketpicks")
    return "\n".join(lines)


def render_eventos_tenis(cards: list[dict[str, Any]]) -> str:
    if not cards:
        return "🎾 *EVENTOS TENIS*\n\nNo hay partidos próximos en cache local."

    grouped: OrderedDict[str, list[dict[str, Any]]] = OrderedDict()
    for card in cards:
        start = card.get("start") or ""
        day = day_label(start) if start else (card.get("day") or "Sin fecha")
        grouped.setdefault(day, []).append(card)

    lines = ["🎾 *EVENTOS TENIS*"]
    for day, items in grouped.items():
        lines.append("")
        lines.append(f"*{day}*")
        for card in items:
            hour = hour_label(card.get("start") or "") if card.get("start") else (card.get("hour") or "--:--")
            title = card.get("title") or "TBD vs TBD"
            tour = card.get("tour") or "Tenis"
            markets = int(card.get("markets") or 0)
            line = f"{hour} - {title} ({tour})"
            if markets > 0:
                line += f" [{markets} markets]"
            lines.append(line)

    lines.append("")
    lines.append("Ver picks: /tenispicks")
    return "\n".join(lines)




def render_tenis_picks(lines: list[str] | None = None) -> str:
    base = [
        "🎾 *TENIS PICKS*",
        "",
        "Base lista; falta capa analítica para picks reales.",
    ]
    if lines:
        extra = [str(x) for x in lines if str(x).strip()]
        if extra:
            base.extend([""] + extra)
    return "\n".join(base)


def rendereventosteniscards(cards: list[dict[str, Any]]) -> str:
    if not cards:
        return "EVENTOS TENIS\nNo hay partidos próximos en cache local."

    grouped: "OrderedDict[str, list[dict[str, Any]]]" = OrderedDict()
    for card in cards:
        start = card.get("start") or ""
        day = daylabel(start) if start else (card.get("day") or "Sin fecha")
        grouped.setdefault(day, []).append(card)

    lines = ["EVENTOS TENIS"]
    for day, items in grouped.items():
        lines.append("")
        lines.append(f"{day}")
        for card in items:
            start = card.get("start") or ""
            hour = hourlabel(start) if start else (card.get("hour") or "--:--")
            title = card.get("title") or "TBD vs TBD"
            tour = card.get("tour") or "Tenis"
            markets = int(card.get("markets") or 0)

            line = f"- {hour} | {title} | {tour}"
            if markets > 0:
                line += f" | {markets} markets"
            lines.append(line)

    lines.append("")
    lines.append("Ver picks: /tenispicks")
    return "\n".join(lines)


def rendereventostenis(cards):
    return rendereventosteniscards(cards)

def format_events_block(title: str, emoji: str, events: list, action_path: str = None) -> str:
    """Formato unificado para eventos deportivos"""
    if not events:
        return f"{emoji} {title.upper()}\n\n*No hay eventos disponibles*\n"
    
    lines = [f"{emoji} {title.upper()}", "🗓️ 09/05/2026", "━━━━━━━━━━━━━━━━━━━━━━"]
    
    # Agrupar por fecha
    by_date = {}
    for event in events:
        date_str = str(event.get('datetime', 'Sin fecha')).split('T')[0]
        if date_str not in by_date:
            by_date[date_str] = []
        by_date[date_str].append(event)
    
    for date_str, date_events in sorted(by_date.items()):
        lines.append(f"\n📅 {date_str}")
        for event in date_events[:10]:  # Top 10 por fecha
            time = str(event.get('datetime', '')).split('T')[1][:5] if 'T' in str(event.get('datetime', '')) else "TBD"
            home = event.get('home', 'TBD')
            away = event.get('away', 'TBD')
            league = event.get('league', 'Sin liga')
            status = event.get('status', 'Pendiente')
            
            line = f"   🕐 {time} | {home} vs {away} | {league} | {status}"
            lines.append(line)
    
    if action_path:
        lines.append(f"\n\n📊 Ver picks → /{action_path}")
    
    return "\n".join(lines)
