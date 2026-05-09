from datetime import timezone

from shared.datetime_utils import parse_datetime, safe_parse_datetime, to_iso


def test_parse_datetime_zulu():
    dt = parse_datetime("2026-05-09T06:32:59Z")
    assert dt.tzinfo == timezone.utc


def test_safe_parse_datetime_invalid():
    assert safe_parse_datetime("fecha rota") is None


def test_to_iso_returns_utc_string():
    text = to_iso("2026-05-09 06:32:59")
    assert text.endswith("+00:00")
