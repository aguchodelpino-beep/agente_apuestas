from __future__ import annotations


def test_handle_futbol_picks_analitica_returns_text():
    from departments.deportes.futbol.analitica_picks_handlers import handle_futbol_picks_analitica
    text = handle_futbol_picks_analitica()
    assert isinstance(text, str)
    assert "FUTBOL PICKS" in text
