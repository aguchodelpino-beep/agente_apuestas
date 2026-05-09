from __future__ import annotations

def self_test() -> bool:
    return True

if __name__ == "__main__":
    if not self_test():
        raise SystemExit("SCRIPT FAIL")
    print("SCRIPT OK")
