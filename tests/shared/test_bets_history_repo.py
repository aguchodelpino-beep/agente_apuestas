from __future__ import annotations

from pathlib import Path

from shared.bets_history_repo import (
    compute_profit,
    ensure_schema,
    list_bets,
    load_bet,
    record_bet,
    settle_bet,
    summarize_by,
    summarize_overall,
)


def test_record_and_load_bet(tmp_path: Path):
    db_path = tmp_path / "bets_history.sqlite"
    ensure_schema(db_path)

    bet_id = record_bet(
        db_path,
        internal_event_id="evt_1",
        sport="futbol",
        league="Premier League",
        market_key="h2h",
        selection_name="Liverpool",
        bookmaker_key="pinnacle",
        odds_taken=1.82,
        stake=10,
        pred_prob=0.61,
        edge_pct=3.2,
        model_name="poisson_v1",
        model_version="2026.05",
    )

    row = load_bet(db_path, bet_id)

    assert row is not None
    assert row["bet_id"] == bet_id
    assert row["sport"] == "futbol"
    assert row["result"] == "pending"
    assert row["odds_taken"] == 1.82


def test_compute_profit_variants():
    assert compute_profit("win", 10, 1.8) == 8.0
    assert compute_profit("loss", 10, 1.8) == -10.0
    assert compute_profit("push", 10, 1.8) == 0.0
    assert compute_profit("half_win", 10, 1.8) == 4.0
    assert compute_profit("half_loss", 10, 1.8) == -5.0


def test_settle_bet_updates_profit_and_closing(tmp_path: Path):
    db_path = tmp_path / "bets_history.sqlite"

    bet_id = record_bet(
        db_path,
        internal_event_id="evt_2",
        sport="tenis",
        league="ATP Roma",
        market_key="match_winner",
        selection_name="Player A",
        bookmaker_key="pinnacle",
        odds_taken=1.75,
        stake=20,
        model_name="elo_surface_v1",
    )

    row = settle_bet(
        db_path,
        bet_id=bet_id,
        result="win",
        closing_odds=1.68,
        settled_at="2026-05-10T12:00:00Z",
    )

    assert row["result"] == "win"
    assert row["closing_odds"] == 1.68
    assert row["profit"] == 15.0
    assert row["settled_at"] == "2026-05-10T12:00:00Z"


def test_summarize_overall_and_by_sport(tmp_path: Path):
    db_path = tmp_path / "bets_history.sqlite"

    bet_futbol = record_bet(
        db_path,
        internal_event_id="evt_3",
        sport="futbol",
        league="Premier League",
        market_key="h2h",
        selection_name="Liverpool",
        bookmaker_key="pinnacle",
        odds_taken=1.80,
        stake=10,
        model_name="poisson_v1",
    )
    settle_bet(db_path, bet_id=bet_futbol, result="win", closing_odds=1.70)

    bet_tenis = record_bet(
        db_path,
        internal_event_id="evt_4",
        sport="tenis",
        league="ATP Roma",
        market_key="match_winner",
        selection_name="Player B",
        bookmaker_key="pinnacle",
        odds_taken=2.10,
        stake=10,
        model_name="elo_surface_v1",
    )
    settle_bet(db_path, bet_id=bet_tenis, result="loss", closing_odds=2.20)

    overall = summarize_overall(db_path)
    by_sport = summarize_by(db_path, "sport")

    assert overall["bets"] == 2
    assert overall["settled_bets"] == 2
    assert overall["total_stake"] == 20.0
    assert overall["total_profit"] == -2.0
    assert overall["roi_pct"] == -10.0
    assert overall["beat_closing_rate_pct"] == 50.0

    futbol = next(row for row in by_sport if row["group_value"] == "futbol")
    tenis = next(row for row in by_sport if row["group_value"] == "tenis")

    assert futbol["total_profit"] == 8.0
    assert tenis["total_profit"] == -10.0


def test_summarize_by_odds_bucket_and_list_bets(tmp_path: Path):
    db_path = tmp_path / "bets_history.sqlite"

    record_bet(
        db_path,
        internal_event_id="evt_5",
        sport="basket",
        league="NBA",
        market_key="spread",
        selection_name="Lakers -4.5",
        bookmaker_key="pinnacle",
        odds_taken=1.91,
        stake=12,
        model_name="ratings_v1",
    )
    record_bet(
        db_path,
        internal_event_id="evt_6",
        sport="basket",
        league="NBA",
        market_key="total",
        selection_name="Over 228.5",
        bookmaker_key="pinnacle",
        odds_taken=2.15,
        stake=8,
        model_name="ratings_v1",
    )

    buckets = summarize_by(db_path, "odds_bucket")
    rows = list_bets(db_path, limit=10, sport="basket")

    group_values = {row["group_value"] for row in buckets}

    assert "1.50-1.99" in group_values
    assert "2.00-2.99" in group_values
    assert len(rows) == 2
    assert all(row["sport"] == "basket" for row in rows)
