from shared.normalizer_engine import (
    build_internal_event_id,
    is_valid_normalized_event,
    normalize_event_payload,
    normalize_league_name,
    normalize_sport_name,
    normalize_start_time,
    normalize_team_name,
)


def test_normalize_team_aliases():
    assert normalize_team_name("Man Utd") == "Manchester United"
    assert normalize_team_name("Barça") == "Barcelona"
    assert normalize_team_name("LA Lakers") == "Los Angeles Lakers"


def test_normalize_league_aliases():
    assert normalize_league_name("EPL") == "Premier League"
    assert normalize_league_name("laliga") == "La Liga"


def test_normalize_sport_aliases():
    assert normalize_sport_name("soccer") == "futbol"
    assert normalize_sport_name("basketball") == "basket"
    assert normalize_sport_name("tennis") == "tenis"


def test_normalize_start_time_to_utc():
    assert normalize_start_time("2026-05-10T14:00:00-05:00") == "2026-05-10T19:00:00Z"


def test_normalize_start_time_empty_returns_none():
    assert normalize_start_time("") is None
    assert normalize_start_time(None) is None


def test_internal_event_id_is_stable():
    first = build_internal_event_id(
        sport="soccer",
        league="EPL",
        home_team="Man Utd",
        away_team="Barça",
        start_time="2026-05-10T14:00:00-05:00",
    )
    second = build_internal_event_id(
        sport="futbol",
        league="Premier League",
        home_team="Manchester United",
        away_team="Barcelona",
        start_time="2026-05-10T19:00:00Z",
    )
    assert first == second
    assert first.startswith("evt_")


def test_normalize_event_payload_builds_complete_shape():
    payload = {
        "sport": "soccer",
        "league": "EPL",
        "home_team": "Man Utd",
        "away_team": "Barça",
        "commence_time": "2026-05-10T19:00:00Z",
    }

    normalized = normalize_event_payload(payload)
    assert normalized["sport"] == "futbol"
    assert normalized["league"] == "Premier League"
    assert normalized["home_team"] == "Manchester United"
    assert normalized["away_team"] == "Barcelona"
    assert normalized["teams"] == ["Manchester United", "Barcelona"]
    assert normalized["internal_event_id"].startswith("evt_")


def test_normalize_event_payload_with_datetime_and_title():
    payload = {
        "sport": "soccer",
        "league": "Soccer",
        "title": "Liverpool vs Chelsea",
        "datetime": "2026-05-09T20:43:00.354484",
    }

    normalized = normalize_event_payload(payload)
    assert normalized["home_team"] == "Liverpool"
    assert normalized["away_team"] == "Chelsea"
    assert normalized["start_time"] == "2026-05-09T20:43:00Z"


def test_is_valid_normalized_event():
    good = {
        "start_time": "2026-05-09T20:43:00Z",
        "home_team": "Liverpool",
        "away_team": "Chelsea",
    }
    bad = {
        "start_time": None,
        "home_team": "TBD",
        "away_team": "Chelsea",
    }
    assert is_valid_normalized_event(good) is True
    assert is_valid_normalized_event(bad) is False
