#!/usr/bin/env bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas
ts="$(date +%Y%m%d_%H%M%S)"

[ -f shared/datetime_utils.py ] && cp shared/datetime_utils.py "shared/datetime_utils.py.bak.$ts"

python - <<'PY'
from pathlib import Path

p = Path("shared/datetime_utils.py")
text = p.read_text(encoding="utf-8")

if "def today_str(" not in text:
    marker = "\n\n__all__ = ["
    block = '''

def now_utc() -> datetime:
    return utc_now()


def today_utc() -> datetime:
    return utc_now().replace(hour=0, minute=0, second=0, microsecond=0)


def today_str() -> str:
    return utc_now().date().isoformat()
'''
    if marker in text:
        text = text.replace(marker, block + marker, 1)
    else:
        text = text.rstrip() + block + "\n"

if '"now_utc"' not in text and "'now_utc'" not in text:
    text = text.replace(
        '__all__ = [',
        '__all__ = [\n    "now_utc",\n    "today_utc",\n    "today_str",',
        1,
    )

p.write_text(text, encoding="utf-8")
PY

python -m py_compile shared/datetime_utils.py

echo "OK patch_datetime_compat"
