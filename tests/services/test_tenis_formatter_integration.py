from departments.visuales.formatter import format_tenis_message
from shared.clv import enrich_pick_with_clv


def test_format_tenis_message_empty():
    out = format_tenis_message([])
    assert "TENIS" in out
    assert "Sin" in out


def test_format_tenis_message_with_items():
    items = [
        {
            "datetime": "2026-05-10T15:00:00Z",
            "home_team": "Alcaraz",
            "away_team": "Djokovic",
            "status": "scheduled",
        }
    ]
    out = format_tenis_message(items)
    assert "Alcaraz" in out
    assert "Djokovic" in out
    assert "15:00" in out


def test_format_tenis_message_with_clv():
    items = [
        {
            "datetime": "2026-05-10T18:00:00Z",
            "home_team": "Sinner",
            "away_team": "Zverev",
            "status": "scheduled",
            "clv": enrich_pick_with_clv(1.80, 1.65),
        }
    ]
    out = format_tenis_message(items)
    assert "Sinner" in out
    assert "📊 CLV" in out
    assert "1.80" in out
    assert "1.65" in out
