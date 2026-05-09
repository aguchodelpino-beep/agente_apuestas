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
