"""
Circuit Breaker Pattern for Agent Safety
Prevents cascading failures by stopping execution when error thresholds are met.
"""

import time
import functools
import logging
from typing import Callable

logger = logging.getLogger(__name__)


class CircuitOpenError(Exception):
    """Raised when the circuit is open (failsafe active)."""

    pass


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED (normal), OPEN (broken), HALF-OPEN (testing)

    def __call__(self, func: Callable):
        """Decorator usage."""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if self.state == "OPEN":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = "HALF-OPEN"
                    logger.info(
                        "Circuit Breaker: Entering HALF-OPEN state (testing recovery)"
                    )
                else:
                    msg = f"Circuit Breaker OPEN. Retrying in {int(self.recovery_timeout - (time.time() - self.last_failure_time))}s"
                    logger.warning(msg)
                    raise CircuitOpenError(msg)

            try:
                result = func(*args, **kwargs)
                if self.state == "HALF-OPEN":
                    self.reset()
                    logger.info("Circuit Breaker: Recovered to CLOSED state")
                return result
            except Exception as e:
                self.record_failure()
                raise e

        return wrapper

    def record_failure(self):
        """Record a failure and potentially trip the circuit."""
        self.failures += 1
        self.last_failure_time = time.time()
        logger.error(
            f"Circuit Breaker: Failure {self.failures}/{self.failure_threshold}"
        )

        if self.failures >= self.failure_threshold:
            self.trip()

    def trip(self):
        """Trip the circuit open."""
        self.state = "OPEN"
        logger.critical("Circuit Breaker: TRIPPED! Stopping all actions.")

    def reset(self):
        """Reset the circuit to normal."""
        self.failures = 0
        self.state = "CLOSED"
