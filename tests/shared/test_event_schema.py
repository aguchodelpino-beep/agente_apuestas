from shared.event_schema import ProviderRef, build_enriched_event


def test_build_enriched_event_includes_provider_map():
    refs = [
        ProviderRef(
            provider="espn",
            provider_event_id="123",
            raw_home_team="Man Utd",
            raw_away_team="Barça",
            raw_league="EPL",
            raw_start_time="2026-05-10T19:00:00Z",
            confidence=0.91,
        )
    ]

    event = build_enriched_event(
        internal_event_id="evt_abc123",
        sport="futbol",
        league="Premier League",
        start_time="2026-05-10T19:00:00Z",
        home_team="Manchester United",
        away_team="Barcelona",
        provider_refs=refs,
    )

    data = event.to_dict()
    assert data["internal_event_id"] == "evt_abc123"
    assert data["teams"] == ["Manchester United", "Barcelona"]
    assert data["provider_map"]["espn"]["provider_event_id"] == "123"
    assert data["provider_map"]["espn"]["confidence"] == 0.91
