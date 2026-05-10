from __future__ import annotations

from pathlib import Path

from departments.analitica.service import build_bets_report
from shared.bets_history_repo import record_bet, settle_bet


def test_build_bets_report_returns_expected_sections(tmp_path: Path):
    db_path = tmp_path / "bets_history.sqlite"

    bet_id = record_bet(
        db_path,
        internal_event_id="evt_srv_1",
        sport="futbol",
        league="La Liga",
        market_key="btts",
        selection_name="Yes",
        bookmaker_key="pinnacle",
        odds_taken=1.95,
        stake=10,
        model_name="poisson_v1",
    )
    settle_bet(db_path, bet_id=bet_id, result="win", closing_odds=1.88)

    report = build_bets_report(db_path)

    assert "overall" in report
    assert "by_sport" in report
    assert "by_league" in report
    assert "by_market" in report
    assert "by_odds_bucket" in report
    assert "by_model" in report
    assert report["overall"]["bets"] == 1
    assert report["by_sport"][0]["group_value"] == "futbol"
