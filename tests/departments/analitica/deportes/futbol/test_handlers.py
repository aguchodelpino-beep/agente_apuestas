from __future__ import annotations

from departments.deportes.futbol.analitica_picks_handlers import handle_futbol_picks_analitica


def test_handle_futbol_picks_analitica_returns_text(monkeypatch):
    monkeypatch.setattr(
        "departments.analitica.deportes.futbol.service.build_futbol_pick_messages",
        lambda **kw: ["⚽ FUTBOL PICKS", "• Match A [Liga] @ 2.10 (EV 15.00%, edge 5.00%) Bet 1.23% → 12.30"],
    )
    text = handle_futbol_picks_analitica()
    assert isinstance(text, str)
    assert "FUTBOL PICKS" in text
