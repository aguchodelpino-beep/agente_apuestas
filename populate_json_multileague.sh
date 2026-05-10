#!/bin/bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas
mkdir -p logs departments/deportes/futbol departments/deportes/basket

python3 - << 'PYEOF'
import os
import json
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path

def load_env_file(path=".env"):
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):]
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v

load_env_file(".env")

multi = os.getenv("ODDSAPIKEYS", "").strip()
single = os.getenv("ODDSAPIKEY", "").strip()
sports = os.getenv("SPORTSAPIKEY", "").strip()

API_KEY = ""
if multi:
    API_KEY = next((k.strip() for k in multi.split(",") if k.strip()), "")
if not API_KEY and single:
    API_KEY = single
if not API_KEY and sports:
    API_KEY = sports

if not API_KEY:
    raise RuntimeError("No existe ODDSAPIKEYS ni ODDSAPIKEY ni SPORTSAPIKEY en .env")

BASE = "https://api.the-odds-api.com/v4/sports"

FUTBOL = {
    "soccer_epl": "Premier League",
    "soccer_spain_la_liga": "La Liga",
    "soccer_germany_bundesliga": "Bundesliga",
    "soccer_italy_serie_a": "Serie A",
    "soccer_france_ligue_one": "Ligue 1",
    "soccer_netherlands_eredivisie": "Eredivisie",
    "soccer_portugal_primeira_liga": "Primeira Liga",
    "soccer_russia_premier_league": "Premier League Rusia",
    "soccer_uefa_champs_league": "Champions League",
    "soccer_uefa_europa_league": "Europa League",
    "soccer_uefa_europa_conference_league": "Conference League",
    "soccer_fa_cup": "FA Cup",
    "soccer_germany_dfb_pokal": "DFB Pokal",
    "soccer_italy_coppa_italia": "Coppa Italia",
    "soccer_france_coupe_de_france": "Coupe de France",
    "soccer_brazil_campeonato": "Brasileirao",
    "soccer_argentina_primera_division": "Primera Division Argentina",
    "soccer_mexico_ligamx": "Liga MX",
    "soccer_colombia_primera_a": "Primera A Colombia",
    "soccer_chile_campeonato": "Primera Division Chile",
    "soccer_ecuador_liga_pro": "LigaPro Ecuador",
    "soccer_conmebol_copa_libertadores": "Copa Libertadores",
    "soccer_conmebol_copa_sudamericana": "Copa Sudamericana",
    "soccer_usa_mls": "MLS",
    "soccer_saudi_arabia_pro_league": "Saudi Pro League",
    "soccer_japan_j_league": "J League",
    "soccer_china_superleague": "Chinese Super League",
    "soccer_korea_kleague1": "K League 1",
    "soccer_australia_aleague": "A-League",
}

BASKET = {
    "basketball_nba": "NBA",
    "basketball_euroleague": "Euroleague",
    "basketball_wnba": "WNBA",
}

def fetch_sport(sport_key, league_name):
    url = f"{BASE}/{sport_key}/odds"
    params = {
        "apiKey": API_KEY,
        "regions": "us,eu",
        "markets": "h2h",
        "oddsFormat": "decimal",
        "dateFormat": "iso",
    }
    try:
        r = requests.get(url, params=params, timeout=25)
        if r.status_code != 200:
            print(f"WARN {sport_key}: status_code={r.status_code}")
            return []
        data = r.json()
    except Exception as e:
        print(f"WARN {sport_key}: {e}")
        return []

    rows = []
    now = datetime.now(timezone.utc)
    limit_end = now + timedelta(days=4)

    for game in data if isinstance(data, list) else []:
        commence = str(game.get("commence_time", "")).replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(commence)
        except Exception:
            continue

        if dt < now - timedelta(hours=4):
            continue
        if dt > limit_end:
            continue

        local_dt = dt.astimezone()
        rows.append({
            "datetime": local_dt.strftime("%Y-%m-%dT%H:%M"),
            "home": game.get("home_team", "TBD"),
            "away": game.get("away_team", "TBD"),
            "league": league_name,
            "status": "Pendiente",
            "sport_key": sport_key,
        })
    return rows

def dedupe(events):
    seen = set()
    out = []
    for e in events:
        k = (e.get("datetime"), e.get("home"), e.get("away"), e.get("league"))
        if k not in seen:
            seen.add(k)
            out.append(e)
    return out

def write_json(path_str, rows):
    path = Path(path_str)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted(rows, key=lambda x: x.get("datetime", ""))[:200]
    path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

futbol_rows = []
for sport_key, league_name in FUTBOL.items():
    futbol_rows.extend(fetch_sport(sport_key, league_name))
futbol_rows = dedupe(futbol_rows)
write_json("departments/deportes/futbol/live_today.json", futbol_rows)

basket_rows = []
for sport_key, league_name in BASKET.items():
    basket_rows.extend(fetch_sport(sport_key, league_name))
basket_rows = dedupe(basket_rows)
write_json("departments/deportes/basket/live_today.json", basket_rows)

print(f"OK futbol: {len(futbol_rows)} eventos")
print(f"OK basket: {len(basket_rows)} eventos")
PYEOF

echo "$(date): populate_json_multileague OK" >> logs/espn.log

sudo systemctl restart telegrambot.service
sleep 2
sudo systemctl status telegrambot.service --no-pager -l
