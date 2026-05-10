import json
from pathlib import Path
from departments.visuales.formatter import format_events_block

ROOT = Path(__file__).resolve().parent

TENIS_JSON = ROOT / "departments" / "deportes" / "tenis" / "live_today.json"
FUTBOL_JSON = ROOT / "departments" / "deportes" / "futbol" / "live_today.json"
BASKET_JSON = ROOT / "departments" / "deportes" / "basket" / "live_today.json"

def _load_events(path: Path, fallback: list[dict]) -> list[dict]:
    try:
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and data:
                    return data
    except Exception:
        pass
    return fallback

def handle_eventos_tenis() -> str:
    fallback = [
        {"datetime": "2026-05-09T14:00", "home": "Flavio Cobolli", "away": "Terence Atmane", "league": "ATP Roma", "status": "Pendiente"},
        {"datetime": "2026-05-09T14:07", "home": "Aryna Sabalenka", "away": "Sorana Cirstea", "league": "WTA Roma", "status": "Pendiente"},
        {"datetime": "2026-05-09T15:15", "home": "Nikoloz Basilashvili", "away": "Ben Shelton", "league": "ATP Roma", "status": "Pendiente"},
        {"datetime": "2026-05-09T16:00", "home": "Frances Tiafoe", "away": "Ignacio Buse", "league": "ATP Roma", "status": "Pendiente"}
    ]
    eventos = _load_events(TENIS_JSON, fallback)
    return format_events_block("Tenis", "🎾", eventos, "tenispicks")

def handle_eventos_futbol() -> str:
    fallback = [
        {"datetime": "2026-05-09T11:30", "home": "Liverpool", "away": "Chelsea", "league": "Premier League", "status": "Pendiente"},
        {"datetime": "2026-05-09T14:00", "home": "Tottenham", "away": "Crystal Palace", "league": "Premier League", "status": "Pendiente"},
        {"datetime": "2026-05-09T16:30", "home": "Manchester City", "away": "Wolves", "league": "Premier League", "status": "Pendiente"},
        {"datetime": "2026-05-09T19:00", "home": "Brighton", "away": "Newcastle", "league": "Premier League", "status": "Pendiente"}
    ]
    eventos = _load_events(FUTBOL_JSON, fallback)
    return format_events_block("Fútbol", "⚽", eventos, "futbolpicks")

def handle_eventos_basket() -> str:
    fallback = [
        {"datetime": "2026-05-09T12:00", "home": "New York Knicks", "away": "Philadelphia 76ers", "league": "NBA Playoffs", "status": "Pendiente"},
        {"datetime": "2026-05-09T14:30", "home": "Minnesota Timberwolves", "away": "Golden State Warriors", "league": "NBA Playoffs", "status": "Pendiente"},
        {"datetime": "2026-05-09T17:00", "home": "Oklahoma City Thunder", "away": "Dallas Mavericks", "league": "NBA Playoffs", "status": "Pendiente"},
        {"datetime": "2026-05-09T22:30", "home": "Los Angeles Lakers", "away": "Denver Nuggets", "league": "NBA Playoffs", "status": "Pendiente"}
    ]
    eventos = _load_events(BASKET_JSON, fallback)
    return format_events_block("Basket", "🏀", eventos, "basketpicks")

if __name__ == "__main__":
    print(handle_eventos_tenis())
    print()
    print(handle_eventos_futbol())
    print()
    print(handle_eventos_basket())
