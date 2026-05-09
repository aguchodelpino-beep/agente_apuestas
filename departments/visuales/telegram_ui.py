from __future__ import annotations

def render_message(text: str) -> dict:
    return {"parse_mode": "Markdown", "text": text}

def self_test() -> bool:
    msg = render_message("Hola")
    return msg.get("parse_mode") == "Markdown"

if __name__ == "__main__":
    assert self_test()
    print("SCRIPT OK")
