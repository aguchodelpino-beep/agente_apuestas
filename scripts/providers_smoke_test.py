#!/usr/bin/env python3
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.providers.tenis_provider import fetch_tennis_events
from shared.providers.futbol_provider import fetch_futbol_events
from shared.providers.basket_provider import fetch_basket_events
from scheduler import refresh_tenis, refresh_futbol, refresh_basket
from departments.deportes.tenis.service import TennisService
from departments.deportes.futbol.service import FutbolService
from departments.deportes.basket.service import BasketService

out = {
    "providers": {
        "tenis": len(fetch_tennis_events()),
        "futbol": len(fetch_futbol_events()),
        "basket": len(fetch_basket_events()),
    },
    "refresh": {
        "tenis": refresh_tenis(),
        "futbol": refresh_futbol(),
        "basket": refresh_basket(),
    },
    "services": {
        "tenis_today": len(TennisService().list_today()),
        "tenis_live": len(TennisService().list_live()),
        "tenis_upcoming": len(TennisService().list_upcoming()),
        "futbol_today": len(FutbolService().list_today()),
        "basket_today": len(BasketService().list_today()),
    },
}
print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
