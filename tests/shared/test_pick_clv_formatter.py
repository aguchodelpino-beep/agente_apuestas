from shared.clv import enrich_pick_with_clv
from shared.pick_clv_formatter import format_pick_clv_line, append_clv_to_pick_text


def test_format_pick_clv_line_with_dict_pick():
    pick = {"clv": enrich_pick_with_clv(2.05, 1.95)}
    out = format_pick_clv_line(pick)
    assert out.startswith("📊 CLV")
    assert "2.05" in out
    assert "1.95" in out


def test_append_clv_to_pick_text():
    pick = {"clv": enrich_pick_with_clv(1.65, 1.55)}
    out = append_clv_to_pick_text("🎾 Alcaraz ML @1.65", pick)
    assert "🎾 Alcaraz ML @1.65" in out
    assert "📊 CLV" in out


def test_append_clv_to_pick_text_without_clv():
    pick = {"market": "h2h"}
    out = append_clv_to_pick_text("⚽ Real Madrid ML @2.20", pick)
    assert out == "⚽ Real Madrid ML @2.20"
