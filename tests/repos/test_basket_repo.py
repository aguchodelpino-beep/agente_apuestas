from departments.deportes.basket.repo import get_fixture_by_id, list_fixtures, list_live_fixtures


def test_list_fixtures():
    assert isinstance(list_fixtures(), list)


def test_list_live_fixtures():
    assert isinstance(list_live_fixtures(), list)


def test_get_fixture_by_id():
    result = get_fixture_by_id("x")
    assert result is None or isinstance(result, dict)
