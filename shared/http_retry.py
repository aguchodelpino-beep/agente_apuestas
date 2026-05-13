from __future__ import annotations

import time
import logging
from enum import Enum
from typing import Callable, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"       # normal, requests pass through
    OPEN = "open"           # failing, requests blocked
    HALF_OPEN = "half_open" # testing recovery


@dataclass
class RetryConfig:
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    backoff_factor: float = 2.0
    retriable_exceptions: tuple = (OSError, TimeoutError)


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    half_open_max_calls: int = 1


@dataclass
class CircuitBreaker:
    name: str
    config: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _failure_count: int = field(default=0, init=False)
    _last_failure_time: float = field(default=0.0, init=False)
    _half_open_calls: int = field(default=0, init=False)

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            if time.monotonic() - self._last_failure_time >= self.config.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0
                logger.info("CircuitBreaker %s → HALF_OPEN", self.name)
        return self._state

    def allow_request(self) -> bool:
        s = self.state
        if s == CircuitState.CLOSED:
            return True
        if s == CircuitState.OPEN:
            return False
        # HALF_OPEN
        if self._half_open_calls < self.config.half_open_max_calls:
            self._half_open_calls += 1
            return True
        return False

    def record_success(self) -> None:
        self._failure_count = 0
        if self._state != CircuitState.CLOSED:
            logger.info("CircuitBreaker %s → CLOSED", self.name)
        self._state = CircuitState.CLOSED

    def record_failure(self) -> None:
        self._failure_count += 1
        self._last_failure_time = time.monotonic()
        if self._failure_count >= self.config.failure_threshold:
            if self._state != CircuitState.OPEN:
                logger.warning(
                    "CircuitBreaker %s → OPEN (fallos=%d)",
                    self.name, self._failure_count,
                )
            self._state = CircuitState.OPEN


class CircuitBreakerOpenError(Exception):
    pass


def with_retry(
    fn: Callable[[], Any],
    config: Optional[RetryConfig] = None,
    circuit_breaker: Optional[CircuitBreaker] = None,
) -> Any:
    cfg = config or RetryConfig()
    delay = cfg.base_delay

    for attempt in range(1, cfg.max_attempts + 1):
        if circuit_breaker and not circuit_breaker.allow_request():
            raise CircuitBreakerOpenError(
                f"CircuitBreaker {circuit_breaker.name!r} OPEN — request bloqueado"
            )
        try:
            result = fn()
            if circuit_breaker:
                circuit_breaker.record_success()
            return result
        except cfg.retriable_exceptions as exc:
            if circuit_breaker:
                circuit_breaker.record_failure()
            if attempt == cfg.max_attempts:
                logger.error(
                    "with_retry: agotados %d intentos. Último error: %s",
                    cfg.max_attempts, exc,
                )
                raise
            logger.warning(
                "with_retry: intento %d/%d falló (%s). Reintentando en %.1fs…",
                attempt, cfg.max_attempts, exc, delay,
            )
            time.sleep(delay)
            delay = min(delay * cfg.backoff_factor, cfg.max_delay)

if __name__ == "__main__":
    print("SCRIPT OK")
