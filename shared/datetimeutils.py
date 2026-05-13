from __future__ import annotations

from datetime import datetime, timezone, timedelta


def _parse_dt(value: str | None) -> datetime | None:
    if not value or not str(value).strip():
        return None
    s = str(value).strip()
    try:
        if s.endswith("Z"):
            return datetime.fromisoformat(s.replace("Z", "+00:00"))
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def todaystr() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


_ECT = timezone(timedelta(hours=-5))  # Ecuador Time UTC-5


def daylabel(value: str | None) -> str:
    dt = _parse_dt(value)
    if not dt:
        return "Sin fecha"
    return dt.astimezone(_ECT).strftime("%Y-%m-%d")


def hourlabel(value: str | None) -> str:
    dt = _parse_dt(value)
    if not dt:
        return "--:--"
    return dt.astimezone(_ECT).strftime("%I:%M %p")

if __name__ == "__main__":
    print("SCRIPT OK")
