#!/usr/bin/env python3
"""
Refresh solo ligas prioritarias de tu lista
"""
import json
from datetime import datetime
from pathlib import Path
from shared.providers.odds_api1_client import fetch_fixtures_by_sport
from shared.league_config import ALL_LEAGUES

today = datetime.now().strftime("%Y-%m-%d")
data_dir = Path("data/raw")

print("🔄 Refresh ligas prioritarias...")
print(f"Target: {len(ALL_LEAGUES)} ligas")

# Sport keys por deporte
sport_keys = {
    "futbol": [10],  # soccer
    "basket": [11],  # basketball  
}

for sport, sport_ids in sport_keys.items():
    for sport_id in sport_ids:
        print(f"\n--- {sport.upper()} sportId={sport_id} ---")
        try:
            fixtures = fetch_fixtures_by_sport(sport_id)
            if fixtures:
                # Filtrar solo tus ligas
                from shared.league_config import filter_events
                priority_fixtures = filter_events(fixtures)
                
                path = data_dir / sport / f"{today}.json"
                path.parent.mkdir(exist_ok=True)
                path.write_text(json.dumps(priority_fixtures, indent=2))
                print(f"✅ {len(priority_fixtures)} ligas prioritarias -> {path}")
            else:
                print("❌ Sin datos")
        except Exception as e:
            print(f"❌ Error: {e}")

print("\n🎯 Ligas prioritarias cacheadas")
