from pathlib import Path

REPO_FILES = [
    Path("departments/deportes/futbol/repo.py"),
    Path("departments/deportes/basket/repo.py"),
    Path("departments/deportes/tenis/repo.py"),
]

FORBIDDEN = [
    "requests.",
    "httpx.",
    "urllib.",
    "provider_",
    "espn_get(",
    "get_odds(",
    "sportsgameodds",
    "rapidapi",
    "the-odds-api",
]

REQUIRED = [
    "load_sport_day",
]

def test_repos_read_from_json_cache_only():
    for path in REPO_FILES:
        text = path.read_text(encoding="utf-8")
        assert any(x in text for x in REQUIRED), f"{path} no parece leer cache local"
        for bad in FORBIDDEN:
            assert bad not in text, f"{path} contiene acceso prohibido: {bad}"
