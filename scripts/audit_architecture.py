from pathlib import Path
import re
import sys

ROOT = Path("/home/aguchodelpino/agente_apuestas")

required_files = [
    ".env",
    "ARCHITECTURE_2_0.md",
    "main.py",
    "core/config.py",
    "core/logging.py",
    "core/health.py",
    "shared/datetime_utils.py",
    "shared/cache.py",
    "shared/odds.py",
    "shared/validators.py",
    "departments/deportes/futbol/handlers.py",
    "departments/deportes/futbol/service.py",
    "departments/deportes/futbol/repo.py",
    "departments/deportes/tenis/handlers.py",
    "departments/deportes/tenis/service.py",
    "departments/deportes/tenis/repo.py",
    "departments/deportes/basket/handlers.py",
    "departments/deportes/basket/service.py",
    "departments/deportes/basket/repo.py",
    "departments/visuales/formatter.py",
    "departments/visuales/markdown.py",
    "departments/visuales/cards.py",
    "departments/visuales/telegram_ui.py",
]

allowed_root_files = {
    ".env",
    "ARCHITECTURE_2_0.md",
    "main.py",
    "telegram_bot.py",
    "telegrambot.py",
    "scheduler.py",
    "handlers.py",
    "sharedoddsnormalizer.py",
    "sharedoddsmath.py",
    "sharedleagueconfig.py",
    "bot.log",
    "pytest.ini",
    "README.md",
}

allowed_root_dirs = {
    "core",
    "departments",
    "shared",
    "scripts",
    "logs",
    "log",
    "cache_diario",
    "cachediario",
    "data",
    "fixtures",
    "tests",
    ".github",
    ".githooks",
    ".git",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "legacy_quarantine",
    "mcp",
    "visuales",
}

import_star_re = re.compile(r'^\s*from\s+[A-Za-z0-9_\.]+\s+import\s+\*', re.MULTILINE)

errors = []

for rel in required_files:
    if not (ROOT / rel).exists():
        errors.append(f"[MISSING] {rel}")

for item in ROOT.iterdir():
    if item.is_file():
        if item.suffix == ".py" and item.name not in allowed_root_files:
            errors.append(f"[ROOT_PY_OUTSIDE] {item.name}")
    elif item.is_dir():
        if item.name not in allowed_root_dirs:
            errors.append(f"[ROOT_DIR_OUTSIDE] {item.name}")

for py in ROOT.rglob("*.py"):
    parts = set(py.parts)
    if ".git" in parts or "venv" in parts or "__pycache__" in parts:
        continue
    text = py.read_text(encoding="utf-8", errors="ignore")
    if import_star_re.search(text):
        errors.append(f"[IMPORT_STAR] {py.relative_to(ROOT)}")

if errors:
    print("ARQUITECTURA INVALIDA")
    for e in errors:
        print(e)
    sys.exit(1)

print("ARQUITECTURA OK")
