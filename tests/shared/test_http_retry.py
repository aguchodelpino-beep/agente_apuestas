from __future__ import annotations

import time
import pytest
from unittest.mock import MagicMock, patch

from shared.http_retry import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpenError,
    CircuitState,
    RetryConfig,
    with_retry,
)


def test_retry_succeeds_on_first_attempt():
    fn = MagicMock(return_value="ok")
    result = with_retry(fn, RetryConfig(max_attempts=3))
    assert result == "ok"
    assert fn.call_count == 1


def test_retry_retries_on_retriable_exception():
    fn = MagicMock(side_effect=[OSError("fallo"), OSError("fallo"), "ok"])
    with patch("shared.http_retry.time.sleep"):
        result = with_retry(fn, RetryConfig(max_attempts=3, base_delay=0.1))
    assert result == "ok"
    assert fn.call_count == 3


def test_retry_raises_after_max_attempts():
    fn = MagicMock(side_effect=OSError("siempre falla"))
    with patch("shared.http_retry.time.sleep"):
        with pytest.raises(OSError):
            with_retry(fn, RetryConfig(max_attempts=3, base_delay=0.1))
    assert fn.call_count == 3


def test_retry_does_not_catch_non_retriable():
    fn = MagicMock(side_effect=ValueError("no retriable"))
    with pytest.raises(ValueError):
        with_retry(fn, RetryConfig(max_attempts=3))
    assert fn.call_count == 1


def test_retry_backoff_delay_increases():
    delays = []

    def capture_sleep(d):
        delays.append(d)

    fn = MagicMock(side_effect=[OSError(), OSError(), "ok"])
    with patch("shared.http_retry.time.sleep", side_effect=capture_sleep):
        with_retry(fn, RetryConfig(max_attempts=3, base_delay=1.0, backoff_factor=2.0))

    assert len(delays) == 2
    assert delays[1] == pytest.approx(2.0)


def test_circuit_starts_closed():
    cb = CircuitBreaker("test")
    assert cb.state == CircuitState.CLOSED


def test_circuit_opens_after_threshold():
    cb = CircuitBreaker("test", CircuitBreakerConfig(failure_threshold=3))
    for _ in range(3):
        cb.record_failure()
    assert cb.state == CircuitState.OPEN


def test_circuit_blocks_when_open():
    cb = CircuitBreaker("test", CircuitBreakerConfig(failure_threshold=1))
    cb.record_failure()
    fn = MagicMock(return_value="ok")
    with pytest.raises(CircuitBreakerOpenError):
        with_retry(fn, circuit_breaker=cb)
    fn.assert_not_called()


def test_circuit_transitions_to_half_open_after_timeout():
    cb = CircuitBreaker(
        "test",
        CircuitBreakerConfig(failure_threshold=1, recovery_timeout=0.01),
    )
    cb.record_failure()
    assert cb.state == CircuitState.OPEN
    time.sleep(0.02)
    assert cb.state == CircuitState.HALF_OPEN


def test_circuit_closes_after_success_in_half_open():
    cb = CircuitBreaker(
        "test",
        CircuitBreakerConfig(failure_threshold=1, recovery_timeout=0.01),
    )
    cb.record_failure()
    time.sleep(0.02)
    cb.record_success()
    assert cb.state == CircuitState.CLOSED


def test_circuit_opens_and_blocks_third_attempt():
    cb = CircuitBreaker("test", CircuitBreakerConfig(failure_threshold=2))
    fn = MagicMock(side_effect=[OSError("fallo1"), OSError("fallo2"), "ok"])
    with patch("shared.http_retry.time.sleep"):
        with pytest.raises(CircuitBreakerOpenError):
            with_retry(fn, RetryConfig(max_attempts=3, base_delay=0.01), circuit_breaker=cb)
    assert cb.state == CircuitState.OPEN
    assert fn.call_count == 2
