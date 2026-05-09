#!/usr/bin/env bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas
ts="$(date +%Y%m%d_%H%M%S)"

[ -f scheduler.py ] && cp scheduler.py "scheduler.py.bak.$ts"

python - <<'PY'
from pathlib import Path
import re

p = Path("scheduler.py")
if not p.exists():
    print("scheduler.py no existe; nada que hacer")
    raise SystemExit(0)

text = p.read_text(encoding="utf-8")

pattern = re.compile(
    r"(def register_example_jobs\(scheduler: BackgroundScheduler\) -> None:\n)(?:    .*\n)+?(?=def |\Z)",
    re.MULTILINE,
)

replacement = (
    "def register_example_jobs(scheduler: BackgroundScheduler) -> None:\n"
    "    # LEGACY DESACTIVADO: la política oficial usa shared/cache_scheduler.py\n"
    "    # con build_all_caches() a las 02:00 America/Guayaquil.\n"
    "    return None\n\n"
)

new_text, n = pattern.subn(replacement, text, count=1)
if n == 0:
    print("No se encontró register_example_jobs; archivo no modificado")
else:
    p.write_text(new_text, encoding="utf-8")
    print("OK legacy scheduler neutralizado")
PY

python -m py_compile scheduler.py
grep -nE 'register_example_jobs|refresh_tenis|refresh_futbol|refresh_basket|add_job' scheduler.py || true
