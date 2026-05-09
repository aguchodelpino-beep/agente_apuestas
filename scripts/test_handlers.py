#!/usr/bin/env python3
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from handlers import (
    handle_eventos_tenis,
    handle_eventos_futbol,
    handle_eventos_basket,
    handle_eventos_por_deporte,
)

out = {
    "tenis_preview": handle_eventos_tenis(),
    "futbol_preview": handle_eventos_futbol(),
    "basket_preview": handle_eventos_basket(),
    "router_tenis": handle_eventos_por_deporte("tenis"),
    "router_futbol": handle_eventos_por_deporte("futbol"),
    "router_basket": handle_eventos_por_deporte("basket"),
}
print(json.dumps(out, ensure_ascii=False, indent=2))
