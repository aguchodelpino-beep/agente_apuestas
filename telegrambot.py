from __future__ import annotations

import os
from pathlib import Path

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

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
        kb = InlineKeyboardMarkup()
        kb.row(
            InlineKeyboardButton("🔄 Actualizar", callback_data="refresh:tenis"),
            InlineKeyboardButton("📊 ROI tenis", callback_data="roi:tenis"),
        )
        bot.reply_to(message, text, parse_mode="Markdown", reply_markup=kb)

    @bot.message_handler(commands=["futbolpicks"])
    def cmd_futbol_picks(message):
        text = handle_futbol_picks()
        kb = InlineKeyboardMarkup()
        kb.row(
            InlineKeyboardButton("🔄 Actualizar", callback_data="refresh:futbol"),
            InlineKeyboardButton("📊 ROI fútbol", callback_data="roi:futbol"),
        )
        bot.reply_to(message, text, parse_mode="Markdown", reply_markup=kb)

    @bot.message_handler(commands=["basketpicks"])
    def cmd_basket_picks(message):
        text = handle_basket_picks()
        kb = InlineKeyboardMarkup()
        kb.row(
            InlineKeyboardButton("🔄 Actualizar", callback_data="refresh:basket"),
            InlineKeyboardButton("📊 ROI basket", callback_data="roi:basket"),
        )
        bot.reply_to(message, text, parse_mode="Markdown", reply_markup=kb)

    @bot.callback_query_handler(func=lambda c: c.data.startswith("refresh:"))
    def cb_refresh(call):
        sport = call.data.split(":")[1]
        bot.answer_callback_query(call.id, f"⏳ Actualizando {sport}...")
        handlers_map = {
            "tenis":  handle_tenis_picks,
            "futbol": handle_futbol_picks,
            "basket": handle_basket_picks,
        }
        fn = handlers_map.get(sport)
        if fn:
            text = fn()
            kb = InlineKeyboardMarkup()
            kb.row(
                InlineKeyboardButton("🔄 Actualizar", callback_data=f"refresh:{sport}"),
                InlineKeyboardButton("📊 ROI", callback_data=f"roi:{sport}"),
            )
            bot.edit_message_text(
                text, call.message.chat.id, call.message.message_id,
                parse_mode="Markdown", reply_markup=kb
            )

    @bot.callback_query_handler(func=lambda c: c.data.startswith("roi:"))
    def cb_roi(call):
        import sys; sys.path.insert(0, ".")
        from shared.roi_query import roi_by, roi_summary
        from shared.bets_history_repo import BETS_DB
        sport = call.data.split(":")[1]
        bot.answer_callback_query(call.id, "📊 Calculando ROI...")
        try:
            rows = roi_by("sport", db_path=BETS_DB)
            summary = roi_summary(db_path=BETS_DB)
            lines = [f"📊 *ROI — {sport.upper()}*"]
            for r in rows:
                if r.value == sport:
                    roi_pct = round((r.pnl / r.staked * 100), 2) if r.staked else 0.0
                    lines.append(
                        f"Apuestas: {r.bets} | Ganadas: {r.won} | Perdidas: {r.lost}\n"
                        f"Stake: {r.staked:.2f} | PnL: {r.pnl:.2f} | ROI: {roi_pct:+.2f}%\n"
                        f"CLV prom: {r.avg_clv:+.2f}%" if hasattr(r, 'avg_clv') else ""
                    )
            if len(lines) == 1:
                lines.append(f"Sin apuestas registradas para {sport}.")
            lines.append(f"\n*Total global:* {summary['total_bets']} bets | PnL: {summary.get('pnl',0):.2f}")
            bot.send_message(call.message.chat.id, "\n".join(lines), parse_mode="Markdown")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ Error ROI: {e}")

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
            "cb_refresh",
            "cb_roi",
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
