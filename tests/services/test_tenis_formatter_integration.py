from departments.deportes.tenis.handlers import handle_eventos_tenis


def test_handle_eventos_tenis_returns_visual_text(monkeypatch):
    monkeypatch.setattr(
        "departments.deportes.tenis.handlers.build_event_cards",
        lambda limit=10: [
            {
                "start": "2026-05-09T15:00:00Z",
                "title": "A vs B",
                "tour": "ATP Rome",
                "markets": 3,
            }
        ],
    )
    text = handle_eventos_tenis()
    assert "EVENTOS TENIS" in text
    assert "A vs B" in text
    assert "ATP Rome" in text


from departments.deportes.tenis.handlers import handle_tenis_picks


def test_handle_tenis_picks_returns_visual_text():
    text = handle_tenis_picks()
    assert "TENIS PICKS" in text
    assert "capa analítica" in text
