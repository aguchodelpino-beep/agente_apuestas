from departments.deportes.tenis import repo


def test_get_today_events_filters_and_sorts(monkeypatch):
    fake_rows = [
        {
            "fixture_id": "late",
            "league": "ATP Roma",
            "home": "Player C",
            "away": "Player D",
            "commence_time": "2026-05-09T18:30:00Z",
        },
        {
            "fixture_id": "today-early",
            "league": "ATP Roma",
            "home": "Player A",
            "away": "Player B",
            "commence_time": "2026-05-09T14:00:00Z",
        },
        {
            "fixture_id": "tomorrow",
            "league": "ATP Roma",
            "home": "Player E",
            "away": "Player F",
            "commence_time": "2026-05-10T10:00:00Z",
        },
        {
            "fixture_id": "nodate",
            "league": "Challenger Turin",
            "home": "Player X",
            "away": "Player Y",
            "commence_time": "",
        },
    ]

    monkeypatch.setattr(repo, "today_str", lambda: "2026-05-09")
    monkeypatch.setattr(repo, "list_fixtures", lambda: fake_rows)

    rows = repo.get_today_events()

    assert [r["fixture_id"] for r in rows] == ["nodate", "today-early", "late"]


def test_get_upcoming_events_applies_limit(monkeypatch):
    fake_rows = [
        {"fixture_id": "b", "league": "ATP Roma", "home": "B", "away": "B2", "commence_time": "2026-05-09T16:00:00Z"},
        {"fixture_id": "a", "league": "ATP Roma", "home": "A", "away": "A2", "commence_time": "2026-05-09T14:00:00Z"},
        {"fixture_id": "c", "league": "ATP Roma", "home": "C", "away": "C2", "commence_time": "2026-05-09T18:00:00Z"},
    ]

    monkeypatch.setattr(repo, "list_fixtures", lambda: fake_rows)

    rows = repo.get_upcoming_events(limit=2)

    assert [r["fixture_id"] for r in rows] == ["a", "b"]


def test_get_events_by_tour_filters_case_insensitive(monkeypatch):
    fake_rows = [
        {"fixture_id": "1", "league": "ATP Roma", "home": "A", "away": "B", "commence_time": "2026-05-09T14:00:00Z"},
        {"fixture_id": "2", "league": "WTA Roma", "home": "C", "away": "D", "commence_time": "2026-05-09T16:00:00Z"},
        {"fixture_id": "3", "league": "Challenger Turin", "home": "E", "away": "F", "commence_time": "2026-05-09T18:00:00Z"},
    ]

    monkeypatch.setattr(repo, "list_fixtures", lambda: fake_rows)

    rows = repo.get_events_by_tour("roma", limit=10)

    assert [r["fixture_id"] for r in rows] == ["1", "2"]


def test_get_fixture_by_id_returns_match(monkeypatch):
    fake_rows = [
        {"fixture_id": "mock-1", "league": "ATP Roma", "home": "A", "away": "B", "commence_time": "2026-05-09T14:00:00Z"},
        {"fixture_id": "mock-2", "league": "WTA Roma", "home": "C", "away": "D", "commence_time": "2026-05-09T16:00:00Z"},
    ]

    monkeypatch.setattr(repo, "list_fixtures", lambda: fake_rows)

    row = repo.get_fixture_by_id("mock-2")

    assert row is not None
    assert row["league"] == "WTA Roma"
    assert row["home"] == "C"
    assert row["away"] == "D"
