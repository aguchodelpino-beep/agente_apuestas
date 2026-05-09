from __future__ import annotations

def build_card(title: str, body: str) -> dict:
    return {"title": title, "body": body}

def self_test() -> bool:
    card = build_card("Tenis", "ATP Rome")
    return card["title"] == "Tenis"

if __name__ == "__main__":
    assert self_test()
    print("SCRIPT OK")
