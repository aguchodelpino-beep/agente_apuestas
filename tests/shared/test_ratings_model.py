from departments.deportes.basket.ratings_model import (
    TeamRatings,
    project_scores,
    ratings_from_event,
)


def test_net_rating_computed():
    t = TeamRatings(team="Lakers", ortg=116.0, drtg=110.0, pace=100.0)
    assert t.net_rtg == 6.0


def test_probabilities_sum_to_one():
    home = TeamRatings("Celtics", ortg=118.0, drtg=108.0, pace=98.0)
    away = TeamRatings("Heat", ortg=112.0, drtg=113.0, pace=97.0)
    r = project_scores(home, away)
    assert abs(r.home_win_prob + r.away_win_prob - 1.0) < 1e-6


def test_better_team_wins_more():
    elite = TeamRatings("Elite", ortg=120.0, drtg=105.0, pace=100.0)
    weak = TeamRatings("Weak", ortg=105.0, drtg=118.0, pace=100.0)
    r = project_scores(elite, weak)
    assert r.home_win_prob > 0.75


def test_projected_total_reasonable():
    home = TeamRatings("A", ortg=115.0, drtg=112.0, pace=100.0)
    away = TeamRatings("B", ortg=113.0, drtg=114.0, pace=100.0)
    r = project_scores(home, away)
    assert 180 < r.projected_total < 260


def test_ratings_from_event_stats():
    event = {
        "home_team": "Bucks",
        "away_team": "Nets",
        "stats": {
            "home_ortg": 116.0,
            "home_drtg": 109.0,
            "home_pace": 101.0,
            "away_ortg": 111.0,
            "away_drtg": 115.0,
            "away_pace": 99.0,
        },
    }
    result = ratings_from_event(event)
    assert result is not None
    home, away = result
    assert home.team == "Bucks"
    assert away.team == "Nets"


def test_ratings_from_event_odds_fallback():
    event = {"odds": {"home": 1.7, "away": 2.2}}
    result = ratings_from_event(event)
    assert result is not None
