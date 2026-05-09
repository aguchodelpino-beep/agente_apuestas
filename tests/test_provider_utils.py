from shared.providers.provider_utils import merge_by_fixture_id, normalize_fixture_row


def test_merge_by_fixture_id():
    a = [{"fixture_id": "1", "x": 1}]
    b = [{"fixture_id": "1", "y": 2}, {"fixture_id": "2", "z": 3}]
    out = merge_by_fixture_id(a, b)
    assert len(out) == 2
    row = [x for x in out if x["fixture_id"] == "1"][0]
    assert row["x"] == 1
    assert row["y"] == 2


def test_normalize_fixture_row():
    row = normalize_fixture_row(
        {"fixtureId": "1", "sport": {"sportName": "futbol"}},
        sport_name="futbol",
        time_field="start_time",
    )
    assert row["fixture_id"] == "1"
    assert row["sport"] == "futbol"
