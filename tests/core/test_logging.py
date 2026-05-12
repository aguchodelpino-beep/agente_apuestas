from __future__ import annotations

import json
import logging
import io

from core.logging import get_logger, setup_logging, JsonFormatter


def test_get_logger_name():
    logger = get_logger("agente_apuestas.test")
    assert logger.name == "agente_apuestas.test"


def test_setup_logging_force():
    setup_logging(force=True)
    logger = get_logger("agente_apuestas.force")
    assert logger is not None


def test_json_formatter_emits_valid_json():
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    logger = logging.getLogger("test_json_basic")
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    logger.info("mensaje de prueba")

    output = stream.getvalue().strip()
    parsed = json.loads(output)
    assert parsed["level"] == "INFO"
    assert parsed["msg"] == "mensaje de prueba"
    assert parsed["logger"] == "test_json_basic"
    assert "ts" in parsed


def test_json_formatter_includes_extra_fields():
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    logger = logging.getLogger("test_json_extra")
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    logger.info("pick generado", extra={"sport": "tenis", "ev_pct": 15.5})

    output = stream.getvalue().strip()
    parsed = json.loads(output)
    assert parsed["sport"] == "tenis"
    assert parsed["ev_pct"] == 15.5


def test_json_formatter_captures_exception():
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    logger = logging.getLogger("test_json_exc")
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    try:
        raise ValueError("error de prueba")
    except ValueError:
        logger.exception("fallo inesperado")

    output = stream.getvalue().strip()
    parsed = json.loads(output)
    assert "exc" in parsed
    assert "ValueError" in str(parsed["exc"])


def test_setup_logging_json_mode(capsys):
    setup_logging(level="DEBUG", force=True, json_output=True)
    logger = get_logger("test_json_mode")
    logger.warning("alerta json")

    captured = capsys.readouterr()
    line = captured.err.strip().splitlines()[-1]
    parsed = json.loads(line)
    assert parsed["level"] == "WARNING"
