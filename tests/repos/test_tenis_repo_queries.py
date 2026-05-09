from departments.deportes.tenis import repo


def test_get_today_events(monkeypatch):
    today = repo.today_str()
    monkeypatch.setattr(
        repo,
        "load_sport_day",
        lambda sport, day: [
            {"fixture_id": "2", "start_time": f"{today}T15:00:00Z", "league": "ATP Rome", "player_1": "B", "player_2": "C"},
            {"fixture_id": "1", "start_time": f"{today}T12:00:00Z", "league": "ATP Rome", "player_1": "A", "player_2": "D"},
        ],
    )
    rows = repo.get_today_events()
    assert [x["fixture_id"] for x in rows] == ["1", "2"]


def test_get_upcoming_events_limit(monkeypatch):
    today = repo.today_str()
    monkeypatch.setattr(
        repo,
        "load_sport_day",
        lambda sport, day: [
            {"fixture_id": "1", "start_time": f"{today}T12:00:00Z", "league": "ATP Rome", "player_1": "A", "player_2": "D"},
            {"fixture_id": "2", "start_time": f"{today}T15:00:00Z", "league": "ATP Rome", "player_1": "B", "player_2": "C"},
            {"fixture_id": "3", "start_time": f"{today}T18:00:00Z", "league": "WTA Rome", "player_1": "E", "player_2": "F"},
        ],
    )
    rows = repo.get_upcoming_events(limit=2)
    assert [x["fixture_id"] for x in rows] == ["1", "2"]


def test_get_events_by_tour(monkeypatch):
    today = repo.today_str()
    monkeypatch.setattr(
        repo,
        "load_sport_day",
        lambda sport, day: [
            {"fixture_id": "1", "start_time": f"{today}T12:00:00Z", "league": "ATP Rome", "player_1": "A", "player_2": "D"},
            {"fixture_id": "2", "start_time": f"{today}T15:00:00Z", "league": "WTA Rome", "player_1": "B", "player_2": "C"},
            {"fixture_id": "3", "start_time": f"{today}T18:00:00Z", "league": "ATP Madrid", "player_1": "E", "player_2": "F"},
        ],
    )
    rows = repo.get_events_by_tour("rome", limit=10)
    assert [x["fixture_id"] for x in rows] == ["1", "2"]
