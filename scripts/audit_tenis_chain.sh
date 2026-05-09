#!/usr/bin/env bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas

echo "=============================="
echo "AUDIT TENIS CHAIN"
echo "=============================="

echo
echo "[1] ARCHIVOS CLAVE"
for f in \
  departments/deportes/tenis/repo.py \
  departments/deportes/tenis/service.py \
  departments/deportes/tenis/handlers.py \
  departments/visuales/formatter.py \
  departments/visuales/markdown.py \
  departments/visuales/telegram_ui.py \
  telegrambot.py \
  telegram_bot.py
do
  if [ -f "$f" ]; then
    echo "OK  $f"
  else
    echo "MISS $f"
  fi
done

echo
echo "[2] IMPORTS Y HOOKS DE TENIS"
grep -RniE 'tenis|tenispicks|eventostenis|get_tenis|get_todos_eventos_tenis|formatter|telegram_ui|markdown' \
  departments/deportes/tenis departments/visuales telegrambot.py telegram_bot.py 2>/dev/null || true

echo
echo "[3] REPO TENIS (TOP 220)"
sed -n '1,220p' departments/deportes/tenis/repo.py 2>/dev/null || true

echo
echo "[4] SERVICE TENIS (TOP 260)"
sed -n '1,260p' departments/deportes/tenis/service.py 2>/dev/null || true

echo
echo "[5] HANDLERS TENIS (TOP 260)"
sed -n '1,260p' departments/deportes/tenis/handlers.py 2>/dev/null || true

echo
echo "[6] VISUALES FORMATTER (TOP 260)"
sed -n '1,260p' departments/visuales/formatter.py 2>/dev/null || true

echo
echo "[7] TELEGRAMBOT referencias tenis"
grep -nE 'eventostenis|tenispicks|get_tenis|get_todos_eventos_tenis|departments.deportes.tenis|formatter|telegram_ui|markdown' \
  telegrambot.py telegram_bot.py 2>/dev/null || true

echo
echo "[8] PY_COMPILE FOCAL"
python -m py_compile \
  departments/deportes/tenis/repo.py \
  departments/deportes/tenis/service.py \
  departments/deportes/tenis/handlers.py \
  departments/visuales/formatter.py \
  departments/visuales/markdown.py \
  departments/visuales/telegram_ui.py \
  telegrambot.py 2>/dev/null || true

python -m py_compile telegram_bot.py 2>/dev/null || true

echo
echo "AUDIT TENIS CHAIN OK"
