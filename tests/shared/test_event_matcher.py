from shared.event_matcher import match_events, match_provider_events


def test_match_events_exact_aliases():
    left = {
        "league": "EPL",
        "sport": "soccer",
        "home_team": "Man Utd",
        "away_team": "Barça",
        "start_time": "2026-05-10T19:00:00Z",
    }
    right = {
        "league": "Premier League",
        "sport": "futbol",
        "home_team": "Manchester United",
        "away_team": "Barcelona",
        "start_time": "2026-05-10T19:20:00Z",
    }

    result = match_events(left, right)
    assert result.matched is True
    assert result.confidence >= 0.82
    assert "league_match" in result.reasons
    assert "home_team_match" in result.reasons
    assert "away_team_match" in result.reasons


def test_match_events_rejects_different_match():
    left = {
        "league": "EPL",
        "sport": "soccer",
        "home_team": "Man Utd",
        "away_team": "Barça",
        "start_time": "2026-05-10T19:00:00Z",
    }
    right = {
        "league": "NBA",
        "sport": "basketball",
        "home_team": "LA Lakers",
        "away_team": "Boston Celtics",
        "start_time": "2026-05-10T19:00:00Z",
    }

    result = match_events(left, right)
    assert result.matched is False


def test_match_provider_events_returns_expected_shape():
    base_events = [
        {
            "provider": "espn",
            "provider_event_id": "123",
            "sport": "soccer",
            "league": "EPL",
            "home_team": "Man Utd",
            "away_team": "Barça",
            "commence_time": "2026-05-10T19:00:00Z",
        }
    ]
    candidate_events = [
        {
            "provider": "oddsapi",
            "provider_event_id": "abc",
            "sport": "futbol",
            "league": "Premier League",
            "home_team": "Manchester United",
            "away_team": "Barcelona",
            "commence_time": "2026-05-10T19:20:00Z",
        }
    ]

    matches = match_provider_events(base_events, candidate_events)
    assert len(matches) == 1
    assert matches[0]["base_provider"] == "espn"
    assert matches[0]["base_provider_id"] == "123"
    assert matches[0]["candidate_provider"] == "oddsapi"
    assert matches[0]["candidate_provider_id"] == "abc"
    assert matches[0]["confidence"] >= 0.82


def test_match_provider_events_skips_non_matches():
    base_events = [
        {
            "provider": "espn",
            "provider_event_id": "123",
            "sport": "soccer",
            "league": "EPL",
            "home_team": "Man Utd",
            "away_team": "Barça",
            "commence_time": "2026-05-10T19:00:00Z",
        }
    ]
    candidate_events = [
        {
            "provider": "oddsapi",
            "provider_event_id": "wrong1",
            "sport": "basketball",
            "league": "NBA",
            "home_team": "LA Lakers",
            "away_team": "Boston Celtics",
            "commence_time": "2026-05-10T19:00:00Z",
        }
    ]

    matches = match_provider_events(base_events, candidate_events)
    assert matches == []


def test_match_provider_events_uses_id_fallback():
    base_events = [
        {
            "provider": "espn",
            "id": "base_evt_1",
            "sport": "soccer",
            "league": "EPL",
            "home_team": "Man Utd",
            "away_team": "Barça",
            "commence_time": "2026-05-10T19:00:00Z",
        }
    ]
    candidate_events = [
        {
            "provider": "pinnacle",
            "id": "cand_evt_1",
            "sport": "futbol",
            "league": "Premier League",
            "home_team": "Manchester United",
            "away_team": "Barcelona",
            "commence_time": "2026-05-10T19:05:00Z",
        }
    ]

    matches = match_provider_events(base_events, candidate_events)
    assert len(matches) == 1
    assert matches[0]["base_provider_id"] == "base_evt_1"
    assert matches[0]["candidate_provider_id"] == "cand_evt_1"


def test_match_provider_events_uses_candidate_once():
    base_events = [
        {
            "provider": "espn",
            "provider_event_id": "base1",
            "sport": "soccer",
            "league": "EPL",
            "home_team": "Man Utd",
            "away_team": "Barça",
            "commence_time": "2026-05-10T19:00:00Z",
        },
        {
            "provider": "espn",
            "provider_event_id": "base2",
            "sport": "soccer",
            "league": "EPL",
            "home_team": "Man Utd",
            "away_team": "Barça",
            "commence_time": "2026-05-10T19:00:00Z",
        },
    ]
    candidate_events = [
        {
            "provider": "oddsapi",
            "provider_event_id": "abc",
            "sport": "futbol",
            "league": "Premier League",
            "home_team": "Manchester United",
            "away_team": "Barcelona",
            "commence_time": "2026-05-10T19:20:00Z",
        }
    ]

    matches = match_provider_events(base_events, candidate_events)
    assert len(matches) == 1
