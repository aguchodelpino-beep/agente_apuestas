#!/usr/bin/env bash
set -euo pipefail
cd /home/aguchodelpino/agente_apuestas

python - <<'PY'
from pathlib import Path

p = Path("departments/visuales/formatter.py")
text = p.read_text(encoding="utf-8")

need = "from shared.datetimeutils import daylabel, hourlabel"

if need in text:
    print("OK: import ya presente")
    raise SystemExit(0)

if "from shared.datetimeutils import hourlabel" in text and "daylabel" not in text:
    text = text.replace("from shared.datetimeutils import hourlabel", need)
elif "from shared.datetimeutils import daylabel" in text and "hourlabel" not in text:
    text = text.replace("from shared.datetimeutils import daylabel", need)
else:
    lines = text.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("from ") or line.startswith("import "):
            insert_at = i + 1
    lines.insert(insert_at, need)
    text = "\n".join(lines) + "\n"

p.write_text(text, encoding="utf-8")
print("OK: import agregado en formatter.py")
PY

python -m py_compile \
  departments/visuales/formatter.py \
  departments/deportes/tenis/handlers.py \
  telegrambot.py

pytest tests/ -v
