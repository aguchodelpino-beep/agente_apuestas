#!/usr/bin/env bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas
exec /home/aguchodelpino/agente_apuestas/venv/bin/python /home/aguchodelpino/agente_apuestas/telegrambot.py >> /home/aguchodelpino/agente_apuestas/logs/telegrambot.log 2>&1
