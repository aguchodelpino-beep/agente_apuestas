#!/bin/bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas
mkdir -p logs

echo "$(date): ESPN status update" >> logs/espn.log

python3 - << 'PYESPN' >> logs/espn.log 2>&1
import requests
import json
from pathlib import Path
from datetime import datetime

def update_live_status(league, json_path):
    url = f"https://site.api.espn.com/apis/site/v2/sports/{league}/scoreboard"
    params = {"dates": datetime.now().strftime("%Y%m%d"), "limit": 50}

    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code != 200:
            print(f"ERROR {league}: status_code={r.status_code}")
            return

        data = r.json()
        events_map = {}

        for event in data.get("events", []):
            competitions = event.get("competitions", [])
            if not competitions:
                continue
            comp = competitions[0]
            teams = comp.get("competitors", [])
            if len(teams) < 2:
                continue

            home = teams[0].get("team", {}).get("displayName", "").strip()
            away = teams[1].get("team", {}).get("displayName", "").strip()
            status = comp.get("status", {}).get("type", {}).get("shortDetail", "")

            if not home or not away:
                continue

            key = f"{home.lower()} vs {away.lower()}"
            if "in progress" in status.lower() or "q" in status.lower() or "set" in status.lower() or "live" in status.lower():
                events_map[key] = "🔴 EN VIVO"
            else:
                events_map[key] = ""

        path = Path(json_path)
        if not path.exists():
            print(f"SKIP {league}: no existe {json_path}")
            return

        with path.open("r", encoding="utf-8") as f:
            events = json.load(f)

        updated = 0
        for event in events:
            home = str(event.get("home", "")).strip().lower()
            away = str(event.get("away", "")).strip().lower()
            key = f"{home} vs {away}"
            if key in events_map:
                event["status"] = events_map[key]
                updated += 1

        with path.open("w", encoding="utf-8") as f:
            json.dump(events, f, indent=2, ensure_ascii=False)

        print(f"OK {league}: actualizados {updated}/{len(events)} en {json_path}")

    except Exception as e:
        print(f"ERROR {league}: {e}")

update_live_status("basketball/nba", "departments/deportes/basket/live_today.json")
update_live_status("soccer/eng.1", "departments/deportes/futbol/live_today.json")
update_live_status("tennis/atp", "departments/deportes/tenis/live_today.json")
PYESPN

sudo systemctl restart telegrambot.service
echo "$(date): ESPN status update done" >> logs/espn.log
