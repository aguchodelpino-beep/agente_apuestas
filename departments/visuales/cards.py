from __future__ import annotations
from typing import Any

SPORT_EMOJI = {"futbol": "⚽", "tenis": "🎾", "basket": "🏀"}

def _edge_badge(ev_pct: float) -> str:
    if ev_pct >= 7.0:  return "🔥 ELITE"
    if ev_pct >= 4.5:  return "⚡ STRONG"
    if ev_pct >= 2.0:  return "🟢 VALUE"
    return "🟡 WEAK"

def _stars(confidence: float) -> str:
    if confidence >= 9.0: return "⭐⭐⭐⭐⭐"
    if confidence >= 7.5: return "⭐⭐⭐⭐"
    if confidence >= 6.0: return "⭐⭐⭐"
    if confidence >= 4.5: return "⭐⭐"
    return "⭐"

def build_card(title: str, body: str, **kwargs) -> dict:
    return {"title": title, "body": body, **kwargs}

def render_pick_card(
    match_title: str, sport: str, league: str, time_str: str,
    pick: str, odds: float, model_prob: float, implied_prob: float,
    ev_pct: float, kelly_pct: float, confidence: float = 0.0,
    market_group: str = "", clv_pct: float | None = None,
) -> str:
    sport_e = SPORT_EMOJI.get((sport or "").lower(), "🏅")
    badge = _edge_badge(ev_pct)
    implied_pct = round(implied_prob * 100, 1) if implied_prob else round(100 / odds, 1) if odds > 1 else 0
    lines = [
        f"{badge}  {sport_e} VALUE BET",
        "━━━━━━━━━━━━━━━━━━━━━━",
        f"🏆 {league}",
        f"{sport_e} {match_title}",
        f"🕒 {time_str}",
        "",
        f"🎯 Pick:    {pick}",
        f"💰 Cuota:   {odds:.2f}",
        "",
        f"📈 Modelo:  {round(model_prob * 100, 1)}%",
        f"📉 Implied: {implied_pct}%",
        f"⚡ Edge:    +{ev_pct:.1f}%",
        "",
        f"🧠 Kelly:   {kelly_pct:.1f}%",
    ]
    if confidence:
        lines.append(f"⭐ Conf:    {_stars(confidence)} ({confidence:.1f}/10)")
    if clv_pct is not None:
        lines.append(f"📊 CLV:     {clv_pct:+.1f}%")
    if market_group:
        lines.append(f"📁 Grupo:   {market_group}")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)

def render_picks_block(picks: list[dict]) -> str:
    if not picks:
        return "🔍 Sin picks disponibles.\n\nFiltros de edge/EV activos."
    header = [
        "🔥 PICKS DEL DÍA",
        "━━━━━━━━━━━━━━━━━━━━━━",
        f"📊 {len(picks)} oportunidad(es) detectada(s)",
        "",
    ]
    cards = []
    for p in picks:
        cards.append(render_pick_card(
            match_title=p.get("match_title") or p.get("event_title") or "Evento",
            sport=p.get("sport", ""),
            league=p.get("league", ""),
            time_str=str(p.get("time_str") or p.get("event_start_time", "TBD"))[:16],
            pick=p.get("selection_name") or p.get("pick", ""),
            odds=float(p.get("odds_taken") or p.get("odds", 0)),
            model_prob=float(p.get("pred_prob") or p.get("model_prob", 0)),
            implied_prob=float(p.get("implied_prob", 0)),
            ev_pct=float(p.get("ev_pct", 0)),
            kelly_pct=float(p.get("fractional_kelly_pct") or p.get("kelly_pct", 0)),
            confidence=float(p.get("confidence", 0)),
            market_group=p.get("_market_group") or p.get("market_group", ""),
            clv_pct=p.get("clv_pct"),
        ))
    return "\n\n".join(header) + "\n\n" + "\n\n".join(cards)

def self_test() -> bool:
    card = render_pick_card(
        match_title="Liverpool vs Tottenham", sport="futbol",
        league="Premier League", time_str="16:00 ECT",
        pick="Over 2.5 Goals", odds=2.08, model_prob=0.61,
        implied_prob=0.48, ev_pct=13.0, kelly_pct=3.5, confidence=8.7,
        market_group="totals",
    )
    return "VALUE BET" in card and "13.0%" in card

if __name__ == "__main__":
    assert self_test()
    print("SCRIPT OK")
