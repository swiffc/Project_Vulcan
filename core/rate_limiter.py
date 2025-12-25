"""
Rate Limiter Middleware - Request Throttling

Thin wrapper around token bucket algorithm for API rate limiting.
Supports per-user, per-endpoint, and global limits.
"""

import time
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
from functools import wraps

logger = logging.getLogger("core.rate_limiter")


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_size: int = 10


@dataclass
class TokenBucket:
    """Token bucket for rate limiting."""
    capacity: float
    tokens: float
    refill_rate: float  # tokens per second
    last_refill: float = field(default_factory=time.time)

    def consume(self, tokens: int = 1) -> Tuple[bool, float]:
        """
        Try to consume tokens.

        Returns:
            Tuple of (allowed, wait_time_seconds)
        """
        now = time.time()
        elapsed = now - self.last_refill

        # Refill tokens
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True, 0.0
        else:
            wait_time = (tokens - self.tokens) / self.refill_rate
            return False, wait_time


class RateLimiter:
    """
    Rate limiter with multiple strategies.

    Supports:
    - Per-user limits
    - Per-endpoint limits
    - Global limits
    - Sliding window
    """

    def __init__(self, config: RateLimitConfig = None):
        self.config = config or RateLimitConfig()
        self._buckets: Dict[str, TokenBucket] = {}
        self._request_log: Dict[str, list] = defaultdict(list)

    def _get_bucket(self, key: str) -> TokenBucket:
        """Get or create token bucket for key."""
        if key not in self._buckets:
            self._buckets[key] = TokenBucket(
                capacity=self.config.burst_size,
                tokens=self.config.burst_size,
                refill_rate=self.config.requests_per_minute / 60.0
            )
        return self._buckets[key]

    def check(self, user_id: str = "global", endpoint: str = None) -> Tuple[bool, Dict]:
        """
        Check if request is allowed.

        Args:
            user_id: User identifier
            endpoint: Optional endpoint for per-route limits

        Returns:
            Tuple of (allowed, metadata)
        """
        key = f"{user_id}:{endpoint}" if endpoint else user_id
        bucket = self._get_bucket(key)

        allowed, wait_time = bucket.consume()

        metadata = {
            "allowed": allowed,
            "remaining": int(bucket.tokens),
            "limit": self.config.requests_per_minute,
            "reset_in": wait_time if not allowed else 0,
        }

        if not allowed:
            logger.warning(f"Rate limit exceeded for {key}, wait {wait_time:.1f}s")

        return allowed, metadata

    def check_hourly(self, user_id: str) -> Tuple[bool, int]:
        """Check hourly limit using sliding window."""
        now = time.time()
        hour_ago = now - 3600

        # Clean old entries
        self._request_log[user_id] = [
            t for t in self._request_log[user_id] if t > hour_ago
        ]

        count = len(self._request_log[user_id])
        allowed = count < self.config.requests_per_hour

        if allowed:
            self._request_log[user_id].append(now)

        return allowed, self.config.requests_per_hour - count

    def reset(self, user_id: str = None):
        """Reset limits for user or all."""
        if user_id:
            keys_to_remove = [k for k in self._buckets if k.startswith(user_id)]
            for k in keys_to_remove:
                del self._buckets[k]
            self._request_log.pop(user_id, None)
        else:
            self._buckets.clear()
            self._request_log.clear()

    def get_headers(self, metadata: Dict) -> Dict[str, str]:
        """Get rate limit headers for response."""
        return {
            "X-RateLimit-Limit": str(metadata.get("limit", 0)),
            "X-RateLimit-Remaining": str(metadata.get("remaining", 0)),
            "X-RateLimit-Reset": str(int(metadata.get("reset_in", 0))),
        }


def rate_limit(limiter: RateLimiter, user_id_func=None):
    """
    Decorator for rate limiting functions.

    Args:
        limiter: RateLimiter instance
        user_id_func: Function to extract user_id from args
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_id = user_id_func(*args, **kwargs) if user_id_func else "global"
            allowed, metadata = limiter.check(user_id, endpoint=func.__name__)

            if not allowed:
                raise RateLimitExceeded(
                    f"Rate limit exceeded. Retry in {metadata['reset_in']:.1f}s",
                    metadata
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""
    def __init__(self, message: str, metadata: Dict):
        super().__init__(message)
        self.metadata = metadata


# Singleton instance
_limiter: Optional[RateLimiter] = None


def get_rate_limiter(config: RateLimitConfig = None) -> RateLimiter:
    """Get or create rate limiter singleton."""
    global _limiter
    if _limiter is None:
        _limiter = RateLimiter(config)
    return _limiter
