from shared.enriched_cache_builder import build_enriched_events


def test_build_enriched_events_merges_matching_provider_records():
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

    enriched = build_enriched_events(base_events, candidate_events)
    assert len(enriched) == 1

    event = enriched[0]
    assert event["home_team"] == "Manchester United"
    assert event["away_team"] == "Barcelona"
    assert event["league"] == "Premier League"
    assert event["internal_event_id"].startswith("evt_")
    assert event["provider_map"]["espn"]["provider_event_id"] == "123"
    assert event["provider_map"]["oddsapi"]["provider_event_id"] == "abc"


def test_build_enriched_events_keeps_unmatched_candidate_as_own_event():
    base_events = []
    candidate_events = [
        {
            "provider": "oddsapi",
            "provider_event_id": "solo1",
            "sport": "basketball",
            "league": "NBA",
            "home_team": "LA Lakers",
            "away_team": "Boston Celtics",
            "commence_time": "2026-05-10T23:00:00Z",
        }
    ]

    enriched = build_enriched_events(base_events, candidate_events)
    assert len(enriched) == 1
    assert enriched[0]["provider_map"]["oddsapi"]["provider_event_id"] == "solo1"
    assert enriched[0]["home_team"] == "Los Angeles Lakers"


def test_build_enriched_events_keeps_unmatched_base_as_own_event():
    base_events = [
        {
            "provider": "espn",
            "provider_event_id": "base1",
            "sport": "tennis",
            "league": "ATP",
            "home_team": "Player A",
            "away_team": "Player B",
            "commence_time": "2026-05-11T15:00:00Z",
        }
    ]
    candidate_events = []

    enriched = build_enriched_events(base_events, candidate_events)
    assert len(enriched) == 1
    assert enriched[0]["provider_map"]["espn"]["provider_event_id"] == "base1"


def test_build_enriched_events_does_not_merge_different_matches():
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

    enriched = build_enriched_events(base_events, candidate_events)
    assert len(enriched) == 2
