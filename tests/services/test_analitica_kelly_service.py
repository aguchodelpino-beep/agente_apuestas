from __future__ import annotations

import pytest

from departments.analitica.models import BetOpportunity, KellyConfig
from departments.analitica.service import (
    evaluate_kelly,
    expected_value_pct,
    full_kelly_pct,
    implied_prob_from_odds,
    kelly_to_bet_record,
)


def test_helper_functions_basic_math():
    assert implied_prob_from_odds(2.0) == 0.5
    assert expected_value_pct(0.55, 2.10) == 15.5
    assert full_kelly_pct(0.55, 2.10) == 14.09


def test_evaluate_kelly_positive_edge_fractional():
    opportunity = BetOpportunity(
        internal_event_id="evt_k1",
        sport="tenis",
        league="ATP Roma",
        market_key="match_winner",
        selection_name="Player A",
        odds_taken=2.10,
        model_prob=0.55,
        bankroll=1000.0,
        model_name="elo_surface_v1",
    )
    config = KellyConfig(
        fractional_kelly=0.25,
        max_stake_pct=0.05,
        min_edge_pct=0.0,
        min_ev_pct=0.0,
        unit_size=5.0,
    )

    decision = evaluate_kelly(opportunity, config)

    assert decision.should_bet is True
    assert decision.full_kelly_pct == 14.09
    assert decision.fractional_kelly_pct == 3.52
    assert decision.capped_stake_pct == 3.52
    assert decision.recommended_stake == 35.2
    assert decision.recommended_units == 7.04
    assert decision.reason == "bet_ok"


def test_evaluate_kelly_respects_cap():
    opportunity = BetOpportunity(
        internal_event_id="evt_k2",
        sport="basket",
        league="NBA",
        market_key="spread",
        selection_name="Lakers -4.5",
        odds_taken=3.00,
        model_prob=0.60,
        bankroll=1000.0,
        model_name="ratings_v1",
    )
    config = KellyConfig(
        fractional_kelly=0.25,
        max_stake_pct=0.02,
    )

    decision = evaluate_kelly(opportunity, config)

    assert decision.should_bet is True
    assert decision.full_kelly_pct == 40.0
    assert decision.fractional_kelly_pct == 10.0
    assert decision.capped_stake_pct == 2.0
    assert decision.recommended_stake == 20.0
    assert decision.reason == "bet_cap_aplicado"


def test_evaluate_kelly_rejects_negative_ev():
    opportunity = BetOpportunity(
        internal_event_id="evt_k3",
        sport="futbol",
        league="Premier League",
        market_key="h2h",
        selection_name="Draw",
        odds_taken=1.80,
        model_prob=0.50,
        bankroll=500.0,
        model_name="poisson_v1",
    )
    config = KellyConfig(
        fractional_kelly=0.25,
        max_stake_pct=0.02,
        min_ev_pct=0.0,
        min_edge_pct=0.0,
    )

    decision = evaluate_kelly(opportunity, config)

    assert decision.should_bet is False
    assert decision.ev_pct == -10.0
    assert decision.recommended_stake == 0.0
    assert decision.reason == "ev_bajo"


def test_kelly_to_bet_record_maps_expected_fields():
    opportunity = BetOpportunity(
        internal_event_id="evt_k4",
        sport="tenis",
        league="ATP Roma",
        market_key="match_winner",
        selection_name="Player B",
        odds_taken=2.05,
        model_prob=0.54,
        bankroll=800.0,
        model_name="elo_surface_v1",
        model_version="2026.05",
        event_start_time="2026-05-10T18:00:00Z",
    )
    decision = evaluate_kelly(opportunity, KellyConfig(fractional_kelly=0.25, max_stake_pct=0.03))

    payload = kelly_to_bet_record(opportunity, decision, ticket_source="tests")

    assert payload["internal_event_id"] == "evt_k4"
    assert payload["sport"] == "tenis"
    assert payload["model_name"] == "elo_surface_v1"
    assert payload["model_version"] == "2026.05"
    assert payload["pred_prob"] == 0.54
    assert payload["stake"] == decision.recommended_stake
    assert payload["ticket_source"] == "tests"


def test_invalid_model_prob_raises():
    with pytest.raises(ValueError):
        BetOpportunity(
            internal_event_id="evt_bad",
            sport="futbol",
            league="La Liga",
            market_key="h2h",
            selection_name="Home",
            odds_taken=1.90,
            model_prob=1.20,
            bankroll=100.0,
        )
