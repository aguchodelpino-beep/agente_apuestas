from __future__ import annotations

import os
from pathlib import Path

import telebot

from handlers import (
    handle_eventos_basket,
    handle_eventos_futbol,
    handle_eventos_tenis,
)
from departments.deportes.futbol.handlers import handle_futbol_picks
from departments.deportes.basket.handlers import handle_basket_picks
from departments.deportes.tenis.handlers import handle_tenis_picks

ROOT = Path(__file__).resolve().parent
ENV_PATH = ROOT / ".env"

def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        os.environ.setdefault(k, v)

_load_env_file(ENV_PATH)

TOKEN = (
    os.getenv("TELEGRAM_BOT_TOKEN")
    or os.getenv("TELEGRAMTOKEN")
    or os.getenv("BOT_TOKEN")
    or os.getenv("TELEGRAM_TOKEN")
)

if not TOKEN:
    raise RuntimeError("No se encontró TELEGRAM_BOT_TOKEN/TELEGRAMTOKEN en .env o entorno")

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

def register_handlers() -> dict:
    @bot.message_handler(commands=["start"])
    def cmd_start(message):
        bot.reply_to(
            message,
            "🤖 Bot activo.\n\nComandos disponibles:\n"
            "/eventostenis\n"
            "/eventosfutbol\n"
            "/eventosbasket\n"
            "/tenispicks\n"
            "/futbolpicks\n"
            "/basketpicks"
        )

    @bot.message_handler(commands=["eventostenis"])
    def cmd_eventos_tenis(message):
        text = handle_eventos_tenis()
        bot.reply_to(message, text, parse_mode="Markdown")

    @bot.message_handler(commands=["eventosfutbol"])
    def cmd_eventos_futbol(message):
        text = handle_eventos_futbol()
        bot.reply_to(message, text, parse_mode="Markdown")

    @bot.message_handler(commands=["eventosbasket"])
    def cmd_eventos_basket(message):
        text = handle_eventos_basket()
        bot.reply_to(message, text, parse_mode="Markdown")

    @bot.message_handler(commands=["tenispicks"])
    def cmd_tenis_picks(message):
        text = handle_tenis_picks()
        bot.reply_to(message, text, parse_mode="Markdown")

    @bot.message_handler(commands=["futbolpicks"])
    def cmd_futbol_picks(message):
        text = handle_futbol_picks()
        bot.reply_to(message, text, parse_mode="Markdown")

    @bot.message_handler(commands=["basketpicks"])
    def cmd_basket_picks(message):
        text = handle_basket_picks()
        bot.reply_to(message, text, parse_mode="Markdown")

    return {
        "status": "ok",
        "handlers": [
            "start",
            "eventostenis",
            "eventosfutbol",
            "eventosbasket",
            "tenispicks",
            "futbolpicks",
            "basketpicks",
        ],
    }

def self_test() -> bool:
    data = register_handlers()
    return data.get("status") == "ok" and len(data.get("handlers", [])) >= 7

def main() -> None:
    register_handlers()
    bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=30)

if __name__ == "__main__":
    assert self_test()
    print("SCRIPT OK")
    main()
