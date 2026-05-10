from __future__ import annotations

from typing import Any, Mapping


def _get(obj: Any, key: str, default=None):
    if isinstance(obj, Mapping):
        return obj.get(key, default)
    return getattr(obj, key, default)


def format_pick_clv_line(pick: Any) -> str:
    clv = _get(pick, "clv")
    if not clv:
        return ""
    describe = _get(clv, "describe")
    if callable(describe):
        text = describe()
    else:
        text = str(clv).strip()
    if not text:
        return ""
    return f"📊 {text}"


def append_clv_to_pick_text(base_text: str, pick: Any) -> str:
    clv_line = format_pick_clv_line(pick)
    if not clv_line:
        return base_text
    return f"{base_text}\n{clv_line}"
