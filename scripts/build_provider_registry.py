#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from shared.providers import ODDS_API_KEYS
from shared.rapidapi_catalog import RAPIDAPI_PRODUCTS

out = {
    "odds_api": {
        "provider": "the_odds_api",
        "rotation_enabled": True,
        "keys_count": len(ODDS_API_KEYS),
        "primary_source": True,
        "fallback_order": ["odds_api", "rapidapi"]
    },
    "rapidapi": {
        "provider": "rapidapi",
        "rotation_enabled": False,
        "products_count": len(RAPIDAPI_PRODUCTS),
        "primary_source": False,
        "status": "catalog_pending_endpoint_discovery",
        "products": RAPIDAPI_PRODUCTS
    }
}

p = Path("/home/aguchodelpino/agente_apuestas/cache_diario/provider_registry.json")
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("OK:", p)
