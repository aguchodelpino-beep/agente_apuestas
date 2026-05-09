from core.logging import get_logger, setup_logging


def test_get_logger_name():
    logger = get_logger("agente_apuestas.test")
    assert logger.name == "agente_apuestas.test"


def test_setup_logging_force():
    setup_logging(force=True)
    logger = get_logger("agente_apuestas.force")
    assert logger is not None
