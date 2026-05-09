#!/usr/bin/env bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas
ts="$(date +%Y%m%d_%H%M%S)"

backup() {
  local f="$1"
  if [ -f "$f" ]; then
    cp "$f" "$f.bak.$ts"
  fi
}

mkdir -p core shared tests/core tests/shared

[ -f core/__init__.py ] || : > core/__init__.py
[ -f shared/__init__.py ] || : > shared/__init__.py

backup core/logging.py
cat > core/logging.py <<'PY'
from __future__ import annotations

import logging
import os
from typing import Optional, Union

DEFAULT_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DEFAULT_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def _resolve_level(level: Optional[Union[str, int]] = None) -> int:
    if isinstance(level, int):
        return level
    value = str(level or DEFAULT_LOG_LEVEL).upper()
    return getattr(logging, value, logging.INFO)


def setup_logging(
    level: Optional[Union[str, int]] = None,
    fmt: str = DEFAULT_LOG_FORMAT,
    force: bool = False,
) -> None:
    logging.basicConfig(
        level=_resolve_level(level),
        format=fmt,
        force=force,
    )


def configure_logging(
    level: Optional[Union[str, int]] = None,
    fmt: str = DEFAULT_LOG_FORMAT,
    force: bool = False,
) -> None:
    setup_logging(level=level, fmt=fmt, force=force)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    root = logging.getLogger()
    if not root.handlers:
        setup_logging()
    return logging.getLogger(name)


__all__ = [
    "DEFAULT_LOG_FORMAT",
    "DEFAULT_LOG_LEVEL",
    "setup_logging",
    "configure_logging",
    "get_logger",
]
PY

backup shared/datetime_utils.py
cat > shared/datetime_utils.py <<'PY'
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


__all__ = [
    "utc_now",
    "ensure_utc",
    "parse_datetime",
    "safe_parse_datetime",
    "to_iso",
    "from_timestamp",
]
PY

backup shared/odds.py
cat > shared/odds.py <<'PY'
from __future__ import annotations

from typing import Union


Number = Union[int, float]


def american_to_prob(odds: Number) -> float:
    odds = float(odds)
    if odds == 0:
        raise ValueError("american odds no puede ser 0")
    if odds < 0:
        return abs(odds) / (abs(odds) + 100.0)
    return 100.0 / (odds + 100.0)


def decimal_to_prob(decimal_odds: Number) -> float:
    decimal_odds = float(decimal_odds)
    if decimal_odds <= 1.0:
        raise ValueError("decimal odds debe ser > 1")
    return 1.0 / decimal_odds


def prob_to_decimal(prob: Number) -> float:
    prob = float(prob)
    if prob <= 0.0 or prob >= 1.0:
        raise ValueError("prob debe estar entre 0 y 1")
    return 1.0 / prob


def edge_percent(model_prob: Number, market_prob: Number) -> float:
    return (float(model_prob) - float(market_prob)) * 100.0


def kelly_fraction(model_prob: Number, decimal_odds: Number, fraction: Number = 1.0) -> float:
    p = float(model_prob)
    d = float(decimal_odds)
    f = float(fraction)

    if p <= 0.0 or p >= 1.0:
        raise ValueError("model_prob debe estar entre 0 y 1")
    if d <= 1.0:
        raise ValueError("decimal_odds debe ser > 1")
    if f <= 0.0:
        raise ValueError("fraction debe ser > 0")

    b = d - 1.0
    q = 1.0 - p
    raw = ((b * p) - q) / b
    return max(0.0, raw * f)


__all__ = [
    "american_to_prob",
    "decimal_to_prob",
    "prob_to_decimal",
    "edge_percent",
    "kelly_fraction",
]
PY

backup tests/core/test_logging.py
cat > tests/core/test_logging.py <<'PY'
from core.logging import get_logger, setup_logging


def test_get_logger_name():
    logger = get_logger("agente_apuestas.test")
    assert logger.name == "agente_apuestas.test"


def test_setup_logging_force():
    setup_logging(force=True)
    logger = get_logger("agente_apuestas.force")
    assert logger is not None
PY

backup tests/shared/test_datetime_utils.py
cat > tests/shared/test_datetime_utils.py <<'PY'
from datetime import timezone

from shared.datetime_utils import parse_datetime, safe_parse_datetime, to_iso


def test_parse_datetime_zulu():
    dt = parse_datetime("2026-05-09T06:32:59Z")
    assert dt.tzinfo == timezone.utc


def test_safe_parse_datetime_invalid():
    assert safe_parse_datetime("fecha rota") is None


def test_to_iso_returns_utc_string():
    text = to_iso("2026-05-09 06:32:59")
    assert text.endswith("+00:00")
PY

backup tests/shared/test_odds.py
cat > tests/shared/test_odds.py <<'PY'
import pytest

from shared.odds import (
    american_to_prob,
    decimal_to_prob,
    edge_percent,
    kelly_fraction,
    prob_to_decimal,
)


def test_decimal_prob_roundtrip():
    assert decimal_to_prob(2.0) == pytest.approx(0.5)
    assert prob_to_decimal(0.5) == pytest.approx(2.0)


def test_kelly_fraction_positive():
    assert kelly_fraction(0.55, 2.10) > 0


def test_american_and_edge():
    assert american_to_prob(-150) == pytest.approx(0.6)
    assert edge_percent(0.55, 0.50) == pytest.approx(5.0)
PY

echo "OK bootstrap_base_pending"
