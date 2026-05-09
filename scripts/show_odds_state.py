#!/usr/bin/env python3
import json
from pathlib import Path

p = Path("/home/aguchodelpino/agente_apuestas/cachediario/odds_api_state.json")
if not p.exists():
    print("SIN_ESTADO")
    raise SystemExit(0)

data = json.loads(p.read_text(encoding="utf-8"))
for key, meta in data.get("keys", {}).items():
    print(
        key[:8],
        "remaining", meta.get("remaining"),
        "used", meta.get("used"),
        "last_status", meta.get("last_status"),
        "cooldown_until", meta.get("cooldown_until"),
    )
