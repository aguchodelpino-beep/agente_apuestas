#!/bin/bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas

echo "== BUSCAR REGISTRO DE COMANDOS =="
grep -RniE "eventosbasket|eventosfutbol|eventostenis|CommandHandler\\(" . \
  --exclude-dir=venv --exclude-dir=.git --exclude-dir=__pycache__ | head -n 300

echo
echo "== BUSCAR IMPORTS DE HANDLERS EN telegrambot.py y handlers.py =="
grep -RniE "deportes\\.basket|deportes\\.futbol|deportes\\.tenis|handlers" telegrambot.py handlers.py 2>/dev/null || true

echo
echo "== LEER telegrambot.py =="
sed -n '1,260p' telegrambot.py 2>/dev/null || true

echo
echo "== LEER handlers.py RAÍZ =="
sed -n '1,260p' handlers.py 2>/dev/null || true

echo
echo "== LEER handlers específicos =="
for f in \
  departments/deportes/basket/handlers.py \
  departments/deportes/futbol/handlers.py \
  departments/deportes/tenis/handlers.py
do
  echo "--- $f ---"
  sed -n '1,220p' "$f" 2>/dev/null || true
done

echo
echo "== DETECTAR ARCHIVOS DUPLICADOS =="
find . -type f \( -name "handlers.py" -o -name "views.py" \) | sort

echo
echo "== JOURNAL ÚLTIMAS 80 LÍNEAS =="
sudo journalctl -u telegrambot.service -n 80 --no-pager -l || true
