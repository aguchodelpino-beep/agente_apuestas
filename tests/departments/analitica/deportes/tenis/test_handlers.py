from __future__ import annotations

from typing import Any

from departments.deportes.tenis.analitica_picks_handlers import handle_tenis_picks_analitica


def test_handle_tenis_picks_analitica_returns_text(monkeypatch):
    monkeypatch.setattr(
        "departments.analitica.deportes.tenis.service.build_tenis_pick_messages",
        lambda **kw: ["🎾 TENIS PICKS", "• Match A @ 2.10 (EV 15.00%, edge 5.00%) Bet 1.23% → 12.30"],
    )

    text = handle_tenis_picks_analitica()
    assert isinstance(text, str)
    assert len(text) > 0
    assert "TENIS PICKS" in text
