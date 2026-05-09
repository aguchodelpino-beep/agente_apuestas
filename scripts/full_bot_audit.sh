#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/aguchodelpino/agente_apuestas"
cd "$ROOT" || exit 1

LOG="logs/full_bot_audit_$(date +%F_%H%M%S).log"
QUAR="legacy_quarantine"
mkdir -p "$QUAR" logs

exec > >(tee -a "$LOG") 2>&1

ok=0
warn=0
fail=0

step() {
  echo
  echo "=================================================="
  echo "$1"
  echo "=================================================="
}

pass() {
  echo "✅ $1"
  ok=$((ok+1))
}

warning() {
  echo "⚠️  $1"
  warn=$((warn+1))
}

error_() {
  echo "❌ $1"
  fail=$((fail+1))
}

spinner_wait() {
  local pid="$1"
  local msg="$2"
  local spin='-\|/'
  local i=0
  while kill -0 "$pid" 2>/dev/null; do
    i=$(( (i+1) %4 ))
    printf "\r[%c] %s" "${spin:$i:1}" "$msg"
    sleep 0.2
  done
  printf "\r[✓] %s\n" "$msg"
}

quarantine_file() {
  local f="$1"
  if [[ -f "$f" ]]; then
    local base
    base="$(basename "$f")"
    local dst="$QUAR/${base}.quarantine_$(date +%s)"
    cp -a "$f" "$dst"
    rm -f "$f"
    warning "Movido a cuarentena y borrado del árbol activo: $f -> $dst"
  fi
}

step "1) ENTORNO"
pwd
python3 --version || true
which python3 || true
if [[ -d venv ]]; then
  pass "venv presente"
else
  error_ "venv no existe"
fi

step "2) ESTRUCTURA CRÍTICA"
for f in main.py scheduler.py handlers.py visuales/markdown.py; do
  if [[ -f "$f" ]]; then
    pass "Existe $f"
  else
    error_ "Falta $f"
  fi
done

for d in shared departments/deportes/tenis departments/deportes/futbol departments/deportes/basket shared/providers; do
  if [[ -d "$d" ]]; then
    pass "Existe directorio $d"
  else
    error_ "Falta directorio $d"
  fi
done

step "3) BUSQUEDA DE ENTRYPOINTS DEL BOT"
find . -maxdepth 2 \( -name "telegrambot.py" -o -name "telegram_bot.py" -o -name "main.py" \) | sed 's#^\./##'
if [[ -f telegrambot.py ]]; then
  pass "Bot principal encontrado: telegrambot.py"
elif [[ -f telegram_bot.py ]]; then
  pass "Bot principal encontrado: telegram_bot.py"
else
  warning "No se encontró archivo bot principal estándar"
fi

step "4) DETECCIÓN DE BASURA / ARCHIVOS PEGADOS MAL"
suspects=()

while IFS= read -r f; do
  [[ "$f" == ./venv/* ]] && continue
  [[ "$f" == ./legacy_quarantine/* ]] && continue

  bad=0

  grep -q "aguchodelpino@agencia-apuestas" "$f" && bad=1 || true
  grep -q "printf '\\\\nOK_" "$f" && bad=1 || true
  grep -q "^>$" "$f" && bad=1 || true
  grep -q "PY'" "$f" && grep -q "Traceback" "$f" && bad=1 || true
  grep -q "No such file or directory" "$f" && bad=1 || true
  grep -q "Requirement already satisfied" "$f" && bad=1 || true

  if [[ "$bad" -eq 1 ]]; then
    suspects+=("$f")
  fi
done < <(find . -type f -name "*.py")

if [[ "${#suspects[@]}" -eq 0 ]]; then
  pass "No se detectó basura evidente en .py"
else
  warning "Archivos sospechosos detectados:"
  printf ' - %s\n' "${suspects[@]}"
fi

step "5) PY_COMPILE GLOBAL"
compile_fail=()
while IFS= read -r f; do
  [[ "$f" == ./venv/* ]] && continue
  [[ "$f" == ./legacy_quarantine/* ]] && continue
  if python3 -m py_compile "$f" >/dev/null 2>&1; then
    echo "OK_COMPILE $f"
  else
    echo "FAIL_COMPILE $f"
    compile_fail+=("$f")
  fi
done < <(find . -type f -name "*.py" | sort)

if [[ "${#compile_fail[@]}" -eq 0 ]]; then
  pass "py_compile limpio en todos los .py activos"
else
  error_ "Fallan py_compile ${#compile_fail[@]} archivos"
  printf ' - %s\n' "${compile_fail[@]}"
fi

step "6) IMPORTS CRÍTICOS"
cat > /tmp/audit_imports.py <<'PY'
import importlib
mods = [
    "scheduler",
    "handlers",
    "visuales.markdown",
    "shared.providers",
    "shared.providers.tenis_provider",
    "shared.providers.futbol_provider",
    "shared.providers.basket_provider",
    "departments.deportes.tenis.repo",
    "departments.deportes.tenis.service",
    "departments.deportes.futbol.repo",
    "departments.deportes.futbol.service",
    "departments.deportes.basket.repo",
    "departments.deportes.basket.service",
]
bad = []
for m in mods:
    try:
        importlib.import_module(m)
        print("IMPORT_OK", m)
    except Exception as e:
        print("IMPORT_FAIL", m, repr(e))
        bad.append((m, repr(e)))
if bad:
    raise SystemExit(1)
PY

if PYTHONPATH=. python3 /tmp/audit_imports.py; then
  pass "Imports críticos OK"
else
  error_ "Fallan imports críticos"
fi

step "7) SMOKE TESTS FUNCIONALES"
if [[ -f scripts/providers_smoke_test.py ]]; then
  if PYTHONPATH=. python3 scripts/providers_smoke_test.py >/tmp/providers_smoke.out 2>/tmp/providers_smoke.err; then
    pass "providers_smoke_test.py OK"
    cat /tmp/providers_smoke.out
  else
    error_ "providers_smoke_test.py falló"
    cat /tmp/providers_smoke.err || true
  fi
else
  warning "No existe scripts/providers_smoke_test.py"
fi

if [[ -f scripts/test_handlers.py ]]; then
  if PYTHONPATH=. python3 scripts/test_handlers.py >/tmp/test_handlers.out 2>/tmp/test_handlers.err; then
    pass "test_handlers.py OK"
    cat /tmp/test_handlers.out
  else
    error_ "test_handlers.py falló"
    cat /tmp/test_handlers.err || true
  fi
else
  warning "No existe scripts/test_handlers.py"
fi

step "8) VALIDACIÓN MAIN/BOT"
if [[ -f main.py ]]; then
  echo "--- main.py (head) ---"
  sed -n '1,80p' main.py
  if grep -q "from scheduler import main" main.py; then
    error_ "main.py importa from scheduler import main, pero scheduler.py actual no expone main()"
  else
    pass "main.py no depende de scheduler.main roto"
  fi
else
  error_ "main.py no existe"
fi

if [[ -f telegrambot.py ]]; then
  echo "--- telegrambot.py handlers eventos ---"
  grep -n "eventostenis\|eventosfutbol\|eventosbasket" telegrambot.py || true
  pass "telegrambot.py presente"
elif [[ -f telegram_bot.py ]]; then
  echo "--- telegram_bot.py handlers eventos ---"
  grep -n "eventostenis\|eventosfutbol\|eventosbasket" telegram_bot.py || true
  pass "telegram_bot.py presente"
else
  warning "No hay archivo bot principal para validar handlers de Telegram"
fi

step "9) CUARENTENA SEGURA"
to_quarantine=()

for f in "${compile_fail[@]:-}"; do
  [[ -n "${f:-}" ]] && to_quarantine+=("$f")
done

for f in "${suspects[@]:-}"; do
  [[ -n "${f:-}" ]] && to_quarantine+=("$f")
done

uniq_quarantine=()
declare -A seen
for f in "${to_quarantine[@]:-}"; do
  [[ -z "${f:-}" ]] && continue
  if [[ -z "${seen[$f]:-}" ]]; then
    seen["$f"]=1
    uniq_quarantine+=("$f")
  fi
done

echo "Candidatos a cuarentena:"
printf ' - %s\n' "${uniq_quarantine[@]:-}" || true

for f in "${uniq_quarantine[@]:-}"; do
  [[ -z "${f:-}" ]] && continue
  case "$f" in
    ./venv/*|./legacy_quarantine/*)
      ;;
    ./main.py|./scheduler.py|./handlers.py|./telegrambot.py|./telegram_bot.py|./visuales/markdown.py)
      warning "NO se cuarentena archivo crítico automáticamente: $f"
      ;;
    *)
      quarantine_file "$f"
      ;;
  esac
done

step "10) REPORTE FINAL"
echo "OK=$ok"
echo "WARN=$warn"
echo "FAIL=$fail"
echo "LOG=$LOG"

if [[ "$fail" -gt 0 ]]; then
  echo "AUDIT_STATUS=FAIL"
  exit 2
else
  echo "AUDIT_STATUS=OK"
fi
