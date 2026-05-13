from __future__ import annotations

import json
import logging as _stdlib_logging
import logging
import os
import traceback
from datetime import datetime, timezone
from typing import Optional, Union

DEFAULT_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DEFAULT_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def _resolve_level(level: Optional[Union[str, int]] = None) -> int:
    if isinstance(level, int):
        return level
    value = str(level or DEFAULT_LOG_LEVEL).upper()
    return getattr(logging, value, logging.INFO)


class JsonFormatter(logging.Formatter):
    """Emite cada log como una línea JSON."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            payload["exc"] = traceback.format_exception(*record.exc_info)
        # campos extra pasados con extra={...}
        for key, val in record.__dict__.items():
            if key not in {
                "msg", "args", "levelname", "levelno", "pathname", "filename",
                "module", "exc_info", "exc_text", "stack_info", "lineno",
                "funcName", "created", "msecs", "relativeCreated", "thread",
                "threadName", "processName", "process", "name", "message",
            }:
                if not key.startswith("_"):
                    payload[key] = val
        return json.dumps(payload, ensure_ascii=False, default=str)


def setup_logging(
    level: Optional[Union[str, int]] = None,
    fmt: str = DEFAULT_LOG_FORMAT,
    force: bool = False,
    json_output: bool = False,
) -> None:
    resolved = _resolve_level(level)
    if json_output:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logging.basicConfig(level=resolved, handlers=[handler], force=force)
    else:
        logging.basicConfig(level=resolved, format=fmt, force=force)


def configure_logging(
    level: Optional[Union[str, int]] = None,
    fmt: str = DEFAULT_LOG_FORMAT,
    force: bool = False,
    json_output: bool = False,
) -> None:
    setup_logging(level=level, fmt=fmt, force=force, json_output=json_output)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    root = logging.getLogger()
    if not root.handlers:
        setup_logging()
    return logging.getLogger(name)


__all__ = [
    "DEFAULT_LOG_FORMAT",
    "DEFAULT_LOG_LEVEL",
    "JsonFormatter",
    "setup_logging",
    "configure_logging",
    "get_logger",
]

if __name__ == "__main__":
    print("SCRIPT OK")
