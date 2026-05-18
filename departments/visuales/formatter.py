from datetime import datetime, timezone, timedelta

_ECT = timezone(timedelta(hours=-5))


def _fmt_dt(dt_str: str):
    """Convierte ISO string UTC → fecha y hora ECT. Retorna (date_str, time_str)."""
    if not dt_str or "T" not in dt_str:
        return "Sin fecha", "TBD"
    try:
        s = dt_str.strip()
        if s.endswith("Z"):
            s = s.replace("Z", "+00:00")
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        dt_ect = dt.astimezone(_ECT)
        return dt_ect.strftime("%d/%m/%Y"), dt_ect.strftime("%I:%M %p")
    except Exception:
        date_str = dt_str.split("T")[0]
        time_str = dt_str.split("T")[1][:5]
        return date_str, time_str


def _fmt_dt_utc_clock(dt_str: str):
    """Retorna fecha y hora HH:MM sin convertir zona horaria."""
    if not dt_str or "T" not in dt_str:
        return "Sin fecha", "TBD"
    try:
        date_str, time_part = dt_str.split("T", 1)
        return date_str, time_part[:5]
    except Exception:
        return "Sin fecha", "TBD"


def render_eventos_basket(cards):
    from datetime import datetime, timezone, timedelta
    now_ect = datetime.now(_ECT)
    lines = [
        "🏀 BASKET — PROXIMOS PARTIDOS",
        f"🗓️ {now_ect.strftime('%d/%m/%Y')}  🕐 ECT (UTC-5)",
        "━━━━━━━━━━━━━━━━━━━━━━",
        ""
    ]

    grouped = {}
    for card in cards or []:
        dt_str = str(card.get("datetime", "") or card.get("start_time", ""))
        date_str, _ = _fmt_dt(dt_str)
        grouped.setdefault(date_str, {})
        league = card.get("league") or "Basket"
        grouped[date_str].setdefault(league, []).append(card)

    for date_str in sorted(grouped.keys(), key=lambda d: datetime.strptime(d, "%d/%m/%Y") if len(d)==10 else datetime.max):
        lines.append(f"📅 {date_str}")
        for league, league_cards in grouped[date_str].items():
            emoji = "🏀" if league == "NBA" else "👟" if league == "WNBA" else "🏀"
            lines.append(f"  {emoji} {league}")
            for card in league_cards:
                dt_str = str(card.get("datetime", "") or card.get("start_time", ""))
                _, time_str = _fmt_dt(dt_str)
                home = card.get("home") or "TBD"
                away = card.get("away") or "TBD"
                status = str(card.get("status", "")).lower()
                live = " 🔴 EN VIVO" if any(s in status for s in ("in", "live", "progress")) else ""
                lines.append(f"   🕐 {time_str}{live} | {home} vs {away}")
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
            status = str(event.get("status") or "").strip()

            base = f"   🕐 {time_str} | {home} vs {away} | {league}"
            if status:
                base += f" | {status}"

            lines.append(base)
        lines.append("")

    if action_path:
        lines.append(f"📊 Ver picks → /{action_path}")

    return "\n".join(lines).strip()


def format_tenis_message(data) -> str:
    """
    Formatea eventos o picks de tenis para Telegram.
    Si los items tienen 'clv', agrega línea de CLV debajo de cada pick.
    """
    from shared.pick_clv_formatter import append_clv_to_pick_text

    if not data:
        return "🎾 TENIS\n\nSin datos disponibles."

    if isinstance(data, str):
        return data

    items = data if isinstance(data, list) else data.get("items", []) if isinstance(data, dict) else []

    if not items:
        return "🎾 TENIS\n\nSin eventos disponibles."

    lines = ["🎾 TENIS — PRÓXIMOS PARTIDOS", "━━━━━━━━━━━━━━━━━━━━━━", ""]

    for item in items[:20]:
        dt = str(item.get("start_time") or item.get("datetime") or item.get("commence_time") or "")
        _, time_str = _fmt_dt_utc_clock(dt)
        home = item.get("home") or item.get("home_team") or item.get("player1") or "TBD"
        away = item.get("away") or item.get("away_team") or item.get("player2") or "TBD"
        status = str(item.get("status") or "").lower()
        live = " 🔴 EN VIVO" if "live" in status or "in_progress" in status else ""
        base = f"🕐 {time_str}{live} | {home} vs {away}"
        lines.append(append_clv_to_pick_text(base, item))
        lines.append("")

    lines.append("📊 Ver picks con EV y Stake -> /tenispicks")
    return "\n".join(lines).strip()
