from shared.providers.provider_utils import safe_get_json, normalize_status


def test_safe_get_json_exists():
    assert callable(safe_get_json)


def test_normalize_status_passthrough():
    assert normalize_status("scheduled") == "scheduled"
