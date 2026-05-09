from __future__ import annotations

from core.logging import get_logger

logger = get_logger(__name__)

def run() -> None:
    logger.info("app_start")
    from telegrambot import main as bot_main
    bot_main()

if __name__ == "__main__":
    run()
