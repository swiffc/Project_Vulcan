"""
Redis Cache Adapter
Caches LLM responses, RAG results, and config to reduce latency and API costs.

Packages Used: redis (pip install redis)
"""

import json
import hashlib
import logging
import os
from typing import Any, Optional
from functools import wraps

logger = logging.getLogger("core.redis-cache")


class RedisCacheAdapter:
    """
    Thin adapter for Redis caching.
    
    Usage:
        cache = RedisCacheAdapter()
        
        # Simple get/set
        cache.set("key", {"data": "value"}, ttl=3600)
        result = cache.get("key")
        
        # Decorator for functions
        @cache.cached(ttl=3600)
        async def expensive_llm_call(prompt):
            ...
    """
    
    def __init__(self, url: str = None):
        self.url = url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self._client = None
        self._available = None
        
    @property
    def client(self):
        """Lazy connection."""
        if self._client is None:
            try:
                import redis
                self._client = redis.from_url(self.url, decode_responses=True)
                self._client.ping()  # Test connection
                self._available = True
                logger.info(f"🔗 Connected to Redis")
            except Exception as e:
                logger.warning(f"Redis unavailable: {e} - using in-memory fallback")
                self._available = False
                self._client = InMemoryCache()
        return self._client
        
    @property
    def available(self) -> bool:
        """Check if Redis is available."""
        if self._available is None:
            _ = self.client  # Trigger connection
        return self._available
        
    def _hash_key(self, key: str) -> str:
        """Create consistent hash for cache keys."""
        return f"vulcan:{hashlib.md5(key.encode()).hexdigest()[:16]}"
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            hashed = self._hash_key(key)
            data = self.client.get(hashed)
            if data:
                logger.debug(f"✅ Cache HIT: {key[:30]}")
                return json.loads(data) if isinstance(data, str) else data
            logger.debug(f"❌ Cache MISS: {key[:30]}")
            return None
        except Exception as e:
            logger.warning(f"Redis get error: {e}")
            return None
            
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL (seconds)."""
        try:
            hashed = self._hash_key(key)
            serialized = json.dumps(value)
            if self._available:
                self.client.setex(hashed, ttl, serialized)
            else:
                self.client.set(hashed, serialized, ttl)
            logger.debug(f"💾 Cached: {key[:30]} (TTL={ttl}s)")
            return True
        except Exception as e:
            logger.warning(f"Redis set error: {e}")
            return False
            
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            self.client.delete(self._hash_key(key))
            return True
        except Exception:
            return False
            
    def cached(self, ttl: int = 3600, prefix: str = ""):
        """Decorator to cache function results."""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Build cache key from function name + args
                key_parts = f"{prefix}{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
                key = key_parts[:200]  # Limit key length
                
                # Check cache
                cached = self.get(key)
                if cached is not None:
                    return cached
                    
                # Call function
                result = await func(*args, **kwargs)
                
                # Cache result
                self.set(key, result, ttl)
                return result
                
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                key_parts = f"{prefix}{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
                key = key_parts[:200]
                
                cached = self.get(key)
                if cached is not None:
                    return cached
                    
                result = func(*args, **kwargs)
                self.set(key, result, ttl)
                return result
                
            # Return appropriate wrapper
            import asyncio
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper
        return decorator
        
    def health(self) -> dict:
        """Check Redis health."""
        try:
            if self._available:
                self.client.ping()
                info = self.client.info("memory")
                return {
                    "status": "healthy",
                    "type": "redis",
                    "used_memory": info.get("used_memory_human", "unknown")
                }
            else:
                return {
                    "status": "healthy",
                    "type": "in-memory-fallback",
                    "note": "Redis unavailable, using local cache"
                }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


class InMemoryCache:
    """Fallback in-memory cache when Redis unavailable."""
    
    def __init__(self, max_size: int = 1000):
        self._cache = {}
        self._expiry = {}
        self._max_size = max_size
        
    def get(self, key: str) -> Optional[str]:
        import time
        if key in self._cache:
            if self._expiry.get(key, float('inf')) > time.time():
                return self._cache[key]
            else:
                del self._cache[key]
                del self._expiry[key]
        return None
        
    def set(self, key: str, value: str, ttl: int = 3600):
        import time
        # Evict oldest if at capacity
        if len(self._cache) >= self._max_size:
            oldest = min(self._expiry, key=self._expiry.get)
            del self._cache[oldest]
            del self._expiry[oldest]
        self._cache[key] = value
        self._expiry[key] = time.time() + ttl
        
    def setex(self, key: str, ttl: int, value: str):
        self.set(key, value, ttl)
        
    def delete(self, key: str):
        self._cache.pop(key, None)
        self._expiry.pop(key, None)
        
    def ping(self):
        return True
        
    def info(self, section: str = None):
        return {"used_memory_human": f"{len(self._cache)} items"}


# Singleton
_cache: Optional[RedisCacheAdapter] = None

def get_cache() -> RedisCacheAdapter:
    global _cache
    if _cache is None:
        _cache = RedisCacheAdapter()
    return _cache
