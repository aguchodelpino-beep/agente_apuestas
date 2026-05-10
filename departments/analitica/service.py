from __future__ import annotations

from pathlib import Path
from typing import Any

from departments.analitica.models import BetOpportunity, KellyConfig, KellyDecision
from shared.bets_history_repo import BETS_DB, summarize_by, summarize_overall


def build_bets_report(db_path: str | Path = BETS_DB) -> dict[str, Any]:
    return {
        "overall": summarize_overall(db_path),
        "by_sport": summarize_by(db_path, "sport"),
        "by_league": summarize_by(db_path, "league"),
        "by_market": summarize_by(db_path, "market_key"),
        "by_odds_bucket": summarize_by(db_path, "odds_bucket"),
        "by_model": summarize_by(db_path, "model_name"),
    }


def implied_prob_from_odds(odds_taken: float) -> float:
    if odds_taken <= 1.0:
        raise ValueError("odds_taken debe ser > 1.0")
    return 1.0 / odds_taken


def expected_value_pct(model_prob: float, odds_taken: float) -> float:
    if not (0.0 <= model_prob <= 1.0):
        raise ValueError("model_prob debe estar entre 0 y 1")
    if odds_taken <= 1.0:
        raise ValueError("odds_taken debe ser > 1.0")
    return round(((model_prob * odds_taken) - 1.0) * 100.0, 2)


def full_kelly_pct(model_prob: float, odds_taken: float) -> float:
    if not (0.0 <= model_prob <= 1.0):
        raise ValueError("model_prob debe estar entre 0 y 1")
    if odds_taken <= 1.0:
        raise ValueError("odds_taken debe ser > 1.0")

    b = odds_taken - 1.0
    q = 1.0 - model_prob
    raw_fraction = ((b * model_prob) - q) / b
    return round(max(0.0, raw_fraction) * 100.0, 2)


def evaluate_kelly(
    opportunity: BetOpportunity,
    config: KellyConfig | None = None,
) -> KellyDecision:
    config = config or KellyConfig()

    implied_prob = round(implied_prob_from_odds(opportunity.odds_taken), 4)
    edge_pct = round((opportunity.model_prob - implied_prob) * 100.0, 2)
    ev_pct = expected_value_pct(opportunity.model_prob, opportunity.odds_taken)
    full_pct = full_kelly_pct(opportunity.model_prob, opportunity.odds_taken)
    fractional_pct = round(full_pct * config.fractional_kelly, 2)
    capped_pct = round(min(fractional_pct, config.max_stake_pct * 100.0), 2)

    should_bet = (
        ev_pct >= config.min_ev_pct
        and edge_pct >= config.min_edge_pct
        and capped_pct > 0.0
    )

    recommended_stake = round(
        opportunity.bankroll * capped_pct / 100.0,
        2,
    ) if should_bet else 0.0

    recommended_units = round(
        recommended_stake / config.unit_size,
        2,
    ) if should_bet else 0.0

    if not should_bet:
        if ev_pct < config.min_ev_pct:
            reason = "ev_bajo"
        elif edge_pct < config.min_edge_pct:
            reason = "edge_bajo"
        else:
            reason = "stake_cero"
    elif capped_pct < fractional_pct:
        reason = "bet_cap_aplicado"
    else:
        reason = "bet_ok"

    return KellyDecision(
        implied_prob=implied_prob,
        edge_pct=edge_pct,
        ev_pct=ev_pct,
        full_kelly_pct=full_pct,
        fractional_kelly_pct=fractional_pct,
        capped_stake_pct=capped_pct,
        recommended_stake=recommended_stake,
        recommended_units=recommended_units,
        should_bet=should_bet,
        reason=reason,
    )


def kelly_to_bet_record(
    opportunity: BetOpportunity,
    decision: KellyDecision,
    *,
    ticket_source: str = "auto_kelly",
) -> dict[str, Any]:
    return {
        "internal_event_id": opportunity.internal_event_id,
        "sport": opportunity.sport,
        "league": opportunity.league,
        "market_key": opportunity.market_key,
        "selection_name": opportunity.selection_name,
        "bookmaker_key": opportunity.bookmaker_key,
        "event_start_time": opportunity.event_start_time,
        "odds_taken": opportunity.odds_taken,
        "stake": decision.recommended_stake,
        "pred_prob": opportunity.model_prob,
        "edge_pct": decision.edge_pct,
        "model_name": opportunity.model_name,
        "model_version": opportunity.model_version,
        "ticket_source": ticket_source,
        "notes": f"ev={decision.ev_pct:.2f};full_kelly={decision.full_kelly_pct:.2f};fractional_kelly={decision.fractional_kelly_pct:.2f}",
    }
