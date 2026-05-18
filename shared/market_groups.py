from __future__ import annotations
from typing import Any

MARKET_GROUPS: dict[str, list[str]] = {
    "moneyline":   ["moneyline_home", "moneyline_away", "moneyline_draw", "h2h", "match_winner", "ML", "DNB"],
    "totals":      ["total_over", "total_under", "btts_yes", "btts_no", "over_2_5", "under_2_5", "Over", "Under", "BTTS"],
    "spread":      ["spread_home", "spread_away", "AH", "Asian Handicap", "Handicap"],
    "team_totals": ["home_total_over", "home_total_under", "away_total_over", "away_total_under"],
    "props":       ["player_prop", "corners", "cards", "assists"],
}

MIN_EDGE_BY_GROUP: dict[str, float] = {
    "moneyline":   0.025,
    "totals":      0.030,
    "spread":      0.025,
    "team_totals": 0.030,
    "props":       0.050,
}


def _get_group(market_key: str) -> str:
    mk = (market_key or "").lower()
    for group, keys in MARKET_GROUPS.items():
        if any(k.lower() in mk or mk in k.lower() for k in keys):
            return group
    return "other"


def select_diversified_picks(
    candidates: list[dict[str, Any]],
    max_picks: int = 3,
    max_per_group: int = 1,
    min_prob: float = 0.53,
) -> list[dict[str, Any]]:
    valid = [
        c for c in candidates
        if float(c.get("model_prob", 0) or 0) >= min_prob
        and float(c.get("ev_pct", 0) or 0) > 0
    ]
    filtered = []
    for c in valid:
        group = _get_group(c.get("market_key", ""))
        min_edge = MIN_EDGE_BY_GROUP.get(group, 0.02)
        edge = float(c.get("edge", c.get("edge_pct", 0)) or 0)
        edge_frac = edge if edge < 1.0 else edge / 100.0
        if edge_frac >= min_edge:
            filtered.append(c)
    filtered.sort(key=lambda x: float(x.get("ev_pct", 0) or 0), reverse=True)
    selected: list[dict] = []
    used_groups: dict[str, int] = {}
    for cand in filtered:
        if len(selected) >= max_picks:
            break
        group = _get_group(cand.get("market_key", ""))
        if used_groups.get(group, 0) >= max_per_group:
            continue
        cand["_market_group"] = group
        selected.append(cand)
        used_groups[group] = used_groups.get(group, 0) + 1
    return selected


if __name__ == "__main__":
    test = [
        {"market_key": "moneyline_home", "ev_pct": 8.0, "edge": 0.05, "model_prob": 0.60},
        {"market_key": "total_over",     "ev_pct": 7.0, "edge": 0.04, "model_prob": 0.58},
        {"market_key": "spread_home",    "ev_pct": 6.0, "edge": 0.03, "model_prob": 0.56},
        {"market_key": "moneyline_away", "ev_pct": 5.0, "edge": 0.03, "model_prob": 0.55},
    ]
    result = select_diversified_picks(test)
    groups = [r["_market_group"] for r in result]
    assert len(groups) == len(set(groups)), "Grupos repetidos!"
    print("SCRIPT OK")
