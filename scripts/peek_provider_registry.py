#!/usr/bin/env python3
from pathlib import Path
p = Path("/home/aguchodelpino/agente_apuestas/cache_diario/provider_registry.json")
print(p.read_text(encoding="utf-8"))
