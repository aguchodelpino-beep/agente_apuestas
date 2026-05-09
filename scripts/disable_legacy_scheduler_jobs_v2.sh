#!/usr/bin/env bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas
ts="$(date +%Y%m%d_%H%M%S)"
cp scheduler.py "scheduler.py.bak.$ts"

python - <<'PY'
from pathlib import Path

p = Path("scheduler.py")
text = p.read_text(encoding="utf-8").replace("\u00a0", "    ")

start = text.find("def register_example_jobs(scheduler: BackgroundScheduler) -> None:")
if start == -1:
    raise SystemExit("ERROR: no se encontró register_example_jobs")

tail = text[start:]
next_def = tail.find("\ndef ", 1)
if next_def == -1:
    end = len(text)
else:
    end = start + next_def + 1

replacement = (
    "def register_example_jobs(scheduler: BackgroundScheduler) -> None:\n"
    "    # LEGACY DESACTIVADO: la política oficial usa shared/cache_scheduler.py\n"
    "    # con build_all_caches() a las 02:00 America/Guayaquil.\n"
    "    return None\n"
)

new_text = text[:start] + replacement + text[end:]
p.write_text(new_text, encoding="utf-8")
print("OK: register_example_jobs neutralizado")
PY

python -m py_compile scheduler.py
grep -nE 'register_example_jobs|refresh_tenis|refresh_futbol|refresh_basket|add_job' scheduler.py || true
