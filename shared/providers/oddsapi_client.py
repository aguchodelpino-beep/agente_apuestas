from __future__ import annotations
from typing import List, Dict, Any
from datetime import datetime, timedelta

def fetch_fixtures(sport_key: str) -> List[Dict[str, Any]]:
    """Simula datos de OddsAPI para todas las ligas."""
    now = datetime.utcnow()
    base_events = [
        {"id": f"{sport_key}_{i}", "datetime": (now + timedelta(hours=i)).isoformat(), "title": f"Partido {i}", "league": sport_key.split('_')[-1].title(), "status": "Pendiente"}
        for i in range(1, 6)
    ]
    return base_events
