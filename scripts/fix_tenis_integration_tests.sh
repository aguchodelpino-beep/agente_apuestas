#!/usr/bin/env bash
set -euo pipefail

cat > tests/services/test_tenis_formatter_integration.py <<'PYEOF'
from departments.deportes.tenis.handlers import handle_eventos_tenis, handle_tenis_picks

def test_handle_eventos_tenis_returns_visual_text():
    text = handle_eventos_tenis()
    assert "TENIS - PRÓXIMOS PARTIDOS" in text
    assert "🗓️" in text
    assert "📊 Ver picks con EV y Stake" in text

def test_handle_tenis_picks_returns_visual_text():
    text = handle_tenis_picks()
    assert "TENIS PICKS" in text
    assert "capa analitica" in text.lower()
PYEOF

pytest tests/services/test_tenis_formatter_integration.py -v
pytest tests/ -v
