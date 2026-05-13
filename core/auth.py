from __future__ import annotations
from core.config import Config

def is_allowed_chat(chat_id: int | str) -> bool:
    if not Config.ALLOWED_CHAT_IDS:
        return True
    return str(chat_id) in {str(x) for x in Config.ALLOWED_CHAT_IDS}

if __name__ == "__main__":
    print("SCRIPT OK")
