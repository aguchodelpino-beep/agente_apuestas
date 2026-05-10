from __future__ import annotations

import os
from pathlib import Path

import telebot

ROOT = Path(__file__).resolve().parent.parent
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


def _get_token() -> str:
    return (
        os.getenv("TELEGRAM_BOT_TOKEN")
        or os.getenv("TELEGRAMTOKEN")
        or os.getenv("BOT_TOKEN")
        or os.getenv("TELEGRAM_TOKEN")
        or ""
    )


def _get_chat_id() -> str:
    return (
        os.getenv("TELEGRAM_CHAT_ID")
        or os.getenv("TELEGRAM_TARGET_CHAT_ID")
        or os.getenv("TELEGRAM_ALERT_CHAT_ID")
        or ""
    )


def send_telegram_message(text: str) -> None:
    token = _get_token()
    chat_id = _get_chat_id()

    if not token:
        raise RuntimeError("Falta TELEGRAM token en entorno/.env")
    if not chat_id:
        raise RuntimeError("Falta TELEGRAM_CHAT_ID en entorno/.env")

    bot = telebot.TeleBot(token, parse_mode="Markdown")
    bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
