from departments.deportes.tenis import repo, service


def test_build_event_cards_with_mock(monkeypatch):
    fake_rows = [
        {
            "fixture_id": "mock-1",
            "sport": "tenis",
            "league": "ATP Roma",
            "home": "Carlos Alcaraz",
            "away": "Jannik Sinner",
            "commence_time": "2026-05-09T14:00:00Z",
            "status": "scheduled",
            "source": "mock",
            "markets": [{"key": "h2h"}],
            "raw": {"shortName": "ATP Roma"},
        },
        {
            "fixture_id": "mock-2",
            "sport": "tenis",
            "league": "WTA Roma",
            "home": "Iga Swiatek",
            "away": "Coco Gauff",
            "commence_time": "2026-05-09T16:30:00Z",
            "status": "scheduled",
            "source": "mock",
            "markets": [{"key": "h2h"}],
            "raw": {"shortName": "WTA Roma"},
        },
    ]

    monkeypatch.setattr(repo, "get_upcoming_events", lambda limit=10: fake_rows[:limit])

    cards = service.build_event_cards(limit=10)

    assert len(cards) == 2

    assert cards[0]["fixture_id"] == "mock-1"
    assert cards[0]["title"] == "Carlos Alcaraz vs Jannik Sinner"
    assert cards[0]["tour"] == "ATP Roma"
    assert cards[0]["start"] == "2026-05-09T14:00:00Z"
    assert cards[0]["status"] == "scheduled"
    assert cards[0]["markets"] == 1
    assert cards[0]["source"] == "mock"

    assert cards[1]["fixture_id"] == "mock-2"
    assert cards[1]["title"] == "Iga Swiatek vs Coco Gauff"
    assert cards[1]["tour"] == "WTA Roma"
    assert cards[1]["start"] == "2026-05-09T16:30:00Z"
    assert cards[1]["status"] == "scheduled"
    assert cards[1]["markets"] == 1
    assert cards[1]["source"] == "mock"


def test_build_event_groups_with_mock(monkeypatch):
    fake_rows = [
        {
            "fixture_id": "mock-1",
            "sport": "tenis",
            "league": "ATP Roma",
            "home": "Carlos Alcaraz",
            "away": "Jannik Sinner",
            "commence_time": "2026-05-09T14:00:00Z",
            "status": "scheduled",
            "source": "mock",
            "markets": [{"key": "h2h"}],
            "raw": {"shortName": "ATP Roma"},
        },
        {
            "fixture_id": "mock-2",
            "sport": "tenis",
            "league": "WTA Roma",
            "home": "Iga Swiatek",
            "away": "Coco Gauff",
            "commence_time": "2026-05-09T16:30:00Z",
            "status": "scheduled",
            "source": "mock",
            "markets": [{"key": "h2h"}],
            "raw": {"shortName": "WTA Roma"},
        },
    ]

    monkeypatch.setattr(repo, "get_upcoming_events", lambda limit=10: fake_rows[:limit])

    groups = service.build_event_groups(limit=10)

    assert len(groups) == 1
    assert groups[0]["day"] == "2026-05-09"
    assert len(groups[0]["items"]) == 2
    assert groups[0]["items"][0]["title"] == "Carlos Alcaraz vs Jannik Sinner"
    assert groups[0]["items"][1]["title"] == "Iga Swiatek vs Coco Gauff"
