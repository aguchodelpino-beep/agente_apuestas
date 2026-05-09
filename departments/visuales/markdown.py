from __future__ import annotations

def to_markdown_title(text: str) -> str:
    return f"# {text.strip()}"

def self_test() -> bool:
    return to_markdown_title("Picks") == "# Picks"

if __name__ == "__main__":
    assert self_test()
    print("SCRIPT OK")
