#!/usr/bin/env bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas || exit 1

for deporte in futbol basket; do
  cat > "departments/deportes/$deporte/models.py" <<PY
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Pick:
    event: str
    market: str
    pick: str
    edge: float = 0.0

def self_test() -> bool:
    item = Pick(event="Test ${deporte}", market="moneyline", pick="A", edge=1.2)
    return item.edge == 1.2

if __name__ == "__main__":
    assert self_test()
    print("SCRIPT OK")
PY

  cat > "departments/deportes/$deporte/repo.py" <<PY
from __future__ import annotations

def list_${deporte}_picks() -> list[dict]:
    return []

def self_test() -> bool:
    data = list_${deporte}_picks()
    return isinstance(data, list)

if __name__ == "__main__":
    assert self_test()
    print("SCRIPT OK")
PY

  cat > "departments/deportes/$deporte/service.py" <<PY
from __future__ import annotations
from departments.deportes.${deporte}.repo import list_${deporte}_picks

def get_${deporte}_picks() -> list[dict]:
    return list_${deporte}_picks()

def self_test() -> bool:
    data = get_${deporte}_picks()
    return isinstance(data, list)

if __name__ == "__main__":
    assert self_test()
    print("SCRIPT OK")
PY

  cat > "departments/deportes/$deporte/handlers.py" <<PY
from __future__ import annotations
from departments.deportes.${deporte}.service import get_${deporte}_picks

def handle_${deporte}_picks() -> list[dict]:
    return get_${deporte}_picks()

def self_test() -> bool:
    data = handle_${deporte}_picks()
    return isinstance(data, list)

if __name__ == "__main__":
    assert self_test()
    print("SCRIPT OK")
PY
done

PYTHONPATH=. venv/bin/python3 -m py_compile departments/deportes/{futbol,basket}/*.py
echo "SCRIPT OK: scripts/patch_futbol_basket_ok.sh"
