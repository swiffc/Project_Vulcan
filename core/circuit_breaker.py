"""
Circuit Breaker Adapter
Prevents runaway automation by cutting connections after threshold errors.

Implements Rule: Section 6 - The Emergency Brake pattern.
Protects bank accounts and CAD files from hallucinating AI.

Packages Used: None (pure Python)
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps

logger = logging.getLogger("core.circuit-breaker")


class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Blocking all calls
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitConfig:
    """Configuration for a circuit breaker."""

    failure_threshold: int = 3  # Failures before opening
    success_threshold: int = 2  # Successes to close from half-open
    timeout_seconds: int = 60  # Time before trying again
    calls_per_minute_limit: int = 10  # Rate limit


@dataclass
class CircuitStats:
    """Statistics for a circuit."""

    total_calls: int = 0
    failures: int = 0
    successes: int = 0
    last_failure: Optional[datetime] = None
    last_success: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    calls_this_minute: int = 0
    minute_started: Optional[datetime] = None


class CircuitBreakerAdapter:
    """
    Circuit breaker to protect against runaway automation.

    Usage:
        breaker = CircuitBreakerAdapter()
        breaker.register("trading", CircuitConfig(failure_threshold=3))

        @breaker.protect("trading")
        async def place_trade(...):
            ...
    """

    def __init__(self):
        self.circuits: Dict[str, CircuitState] = {}
        self.configs: Dict[str, CircuitConfig] = {}
        self.stats: Dict[str, CircuitStats] = {}

    def register(self, name: str, config: CircuitConfig = None) -> None:
        """Register a new circuit."""
        self.circuits[name] = CircuitState.CLOSED
        self.configs[name] = config or CircuitConfig()
        self.stats[name] = CircuitStats()
        logger.info(f"⚡ Registered circuit: {name}")

    def protect(self, circuit_name: str):
        """Decorator to protect a function with circuit breaker."""

        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await self._execute(circuit_name, func, *args, **kwargs)

            return wrapper

        return decorator

    async def _execute(self, name: str, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if name not in self.circuits:
            self.register(name)

        state = self.circuits[name]
        config = self.configs[name]
        stats = self.stats[name]

        # Check rate limit
        if not self._check_rate_limit(name):
            raise CircuitBreakerError(f"Rate limit exceeded for {name}")

        # Check circuit state
        if state == CircuitState.OPEN:
            if self._should_attempt_reset(name):
                self.circuits[name] = CircuitState.HALF_OPEN
                logger.info(f"🔄 Circuit {name} entering half-open state")
            else:
                raise CircuitBreakerError(f"Circuit {name} is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._record_success(name)
            return result
            return result
        except Exception as e:
            self._record_failure(name)
            raise

    async def run_with_fallback(
        self, name: str, func: Callable, fallback_func: Callable, *args, **kwargs
    ) -> Any:
        """
        Run a function with circuit breaker protection and a fallback.

        Args:
            name: Circuit name
            func: Primary function to execute
            fallback_func: Function to execute if primary fails or circuit is open
            args, kwargs: Arguments for both functions

        Returns:
            Result of func or fallback_func
        """
        try:
            return await self._execute(name, func, *args, **kwargs)
        except (CircuitBreakerError, Exception) as e:
            logger.warning(
                f"Circuit {name} interrupted/failed: {e}. Executing fallback."
            )
            return await fallback_func(*args, **kwargs)

    def _check_rate_limit(self, name: str) -> bool:
        """Check if within rate limit."""
        stats = self.stats[name]
        config = self.configs[name]
        now = datetime.utcnow()

        # Reset minute counter if new minute
        if stats.minute_started is None or (now - stats.minute_started).seconds >= 60:
            stats.minute_started = now
            stats.calls_this_minute = 0

        stats.calls_this_minute += 1
        return stats.calls_this_minute <= config.calls_per_minute_limit

    def _should_attempt_reset(self, name: str) -> bool:
        """Check if enough time passed to try again."""
        stats = self.stats[name]
        config = self.configs[name]

        if stats.opened_at is None:
            return True

        elapsed = (datetime.utcnow() - stats.opened_at).seconds
        return elapsed >= config.timeout_seconds

    def _record_success(self, name: str) -> None:
        """Record successful call."""
        stats = self.stats[name]
        config = self.configs[name]

        stats.total_calls += 1
        stats.successes += 1
        stats.last_success = datetime.utcnow()
        stats.failures = 0  # Reset consecutive failures

        # Close circuit if in half-open and enough successes
        if self.circuits[name] == CircuitState.HALF_OPEN:
            if stats.successes >= config.success_threshold:
                self.circuits[name] = CircuitState.CLOSED
                stats.opened_at = None
                logger.info(f"✅ Circuit {name} CLOSED (recovered)")

    def _record_failure(self, name: str) -> None:
        """Record failed call."""
        stats = self.stats[name]
        config = self.configs[name]

        stats.total_calls += 1
        stats.failures += 1
        stats.last_failure = datetime.utcnow()

        # Open circuit if threshold reached
        if stats.failures >= config.failure_threshold:
            self.circuits[name] = CircuitState.OPEN
            stats.opened_at = datetime.utcnow()
            logger.warning(f"🛑 Circuit {name} OPENED after {stats.failures} failures")

    def get_status(self) -> Dict[str, Dict]:
        """Get status of all circuits."""
        return {
            name: {
                "state": self.circuits[name].value,
                "failures": self.stats[name].failures,
                "total_calls": self.stats[name].total_calls,
            }
            for name in self.circuits
        }

    def reset(self, name: str) -> None:
        """Manually reset a circuit."""
        if name in self.circuits:
            self.circuits[name] = CircuitState.CLOSED
            self.stats[name] = CircuitStats()
            logger.info(f"🔄 Circuit {name} manually reset")


class CircuitBreakerError(Exception):
    """Raised when circuit breaker blocks a call."""

    pass


# Singleton instance
_breaker: Optional[CircuitBreakerAdapter] = None


def get_circuit_breaker() -> CircuitBreakerAdapter:
    """Get or create circuit breaker singleton."""
    global _breaker
    if _breaker is None:
        _breaker = CircuitBreakerAdapter()
        # Register default circuits
        _breaker.register(
            "trading", CircuitConfig(failure_threshold=3, calls_per_minute_limit=5)
        )
        _breaker.register(
            "cad", CircuitConfig(failure_threshold=5, calls_per_minute_limit=10)
        )
        _breaker.register(
            "desktop", CircuitConfig(failure_threshold=10, calls_per_minute_limit=60)
        )
    return _breaker
