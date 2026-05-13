from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Union


DateInput = Union[str, datetime]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def parse_datetime(value: DateInput) -> datetime:
    if isinstance(value, datetime):
        return ensure_utc(value)

    text = str(value).strip()
    if not text:
        raise ValueError("datetime vacío")

    if text.endswith("Z"):
        text = text[:-1] + "+00:00"

    try:
        return ensure_utc(datetime.fromisoformat(text))
    except ValueError:
        pass

    formats = (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    )
    for fmt in formats:
        try:
            return ensure_utc(datetime.strptime(text, fmt))
        except ValueError:
            continue

    raise ValueError(f"datetime inválido: {value!r}")


def safe_parse_datetime(value: Optional[DateInput]) -> Optional[datetime]:
    if value is None:
        return None
    try:
        return parse_datetime(value)
    except (TypeError, ValueError):
        return None


def to_iso(value: DateInput) -> str:
    return parse_datetime(value).isoformat()


def from_timestamp(value: Union[int, float]) -> datetime:
    return datetime.fromtimestamp(float(value), tz=timezone.utc)


def now_utc() -> datetime:
    return utc_now()


def today_utc() -> datetime:
    return utc_now().replace(hour=0, minute=0, second=0, microsecond=0)


def today_str() -> str:
    return utc_now().date().isoformat()


__all__ = [
    "now_utc",
    "today_utc",
    "today_str",
    "utc_now",
    "ensure_utc",
    "parse_datetime",
    "safe_parse_datetime",
    "to_iso",
    "from_timestamp",
]

def day_label(value):
    if value is None:
        return ''
    return str(value)[:10]


def hour_label(value):
    if value is None:
        return ''
    s = str(value)
    if 'T' in s and len(s) >= 16:
        return s[11:16]
    return s[:5]


if __name__ == "__main__":
    print("SCRIPT OK")
