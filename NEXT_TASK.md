# NEXT TASK FOR CLI

**From**: Claude Chat
**Priority**: High
**Type**: New Feature - Redis Cache Adapter

---

## 📋 TASK: Add Redis Caching Layer

### WHY
- Speed up repeated queries (50ms vs 2-3 sec)
- Reduce Claude API costs (cache hits = free)
- Follow Elite Engineering patterns from RULES.md

### WHAT TO BUILD

#### 1. Create `agents/core/redis_adapter.py` (~100-150 lines)

```python
"""
Redis Cache Adapter
Caches LLM responses, RAG results, and config to reduce latency and API costs.

Packages Used: redis (pip install redis)
"""

import json
import hashlib
import logging
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
        # Lazy import
        import redis
        import os
        
        self.url = url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self._client = None
        
    @property
    def client(self):
        """Lazy connection."""
        if self._client is None:
            import redis
            self._client = redis.from_url(self.url, decode_responses=True)
            logger.info(f"🔗 Connected to Redis: {self.url[:20]}...")
        return self._client
        
    def _hash_key(self, key: str) -> str:
        """Create consistent hash for cache keys."""
        return f"vulcan:{hashlib.md5(key.encode()).hexdigest()[:16]}"
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            data = self.client.get(self._hash_key(key))
            if data:
                logger.debug(f"✅ Cache HIT: {key[:30]}")
                return json.loads(data)
            logger.debug(f"❌ Cache MISS: {key[:30]}")
            return None
        except Exception as e:
            logger.warning(f"Redis get error: {e}")
            return None
            
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL (seconds)."""
        try:
            self.client.setex(
                self._hash_key(key),
                ttl,
                json.dumps(value)
            )
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
            async def wrapper(*args, **kwargs):
                # Build cache key from function name + args
                key = f"{prefix}{func.__name__}:{str(args)}:{str(kwargs)}"
                
                # Check cache
                cached = self.get(key)
                if cached is not None:
                    return cached
                    
                # Call function
                result = await func(*args, **kwargs)
                
                # Cache result
                self.set(key, result, ttl)
                return result
            return wrapper
        return decorator
        
    def health(self) -> dict:
        """Check Redis health."""
        try:
            self.client.ping()
            info = self.client.info("memory")
            return {
                "status": "healthy",
                "used_memory": info.get("used_memory_human", "unknown")
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


# Singleton
_cache: Optional[RedisCacheAdapter] = None

def get_cache() -> RedisCacheAdapter:
    global _cache
    if _cache is None:
        _cache = RedisCacheAdapter()
    return _cache
```

#### 2. Update `docker-compose.yml` - Add Redis service

```yaml
  # Add this service
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped
    networks:
      - vulcan-net

# Add to volumes section
volumes:
  redis-data:
```

#### 3. Update `requirements.txt` - Add redis package

```
redis==5.0.1
```

#### 4. Update `render.yaml` - Add Render Redis

```yaml
  # Add Redis service
  - type: redis
    name: vulcan-redis
    plan: free
    maxmemoryPolicy: allkeys-lru
```

And update orchestrator envVars:
```yaml
      - key: REDIS_URL
        fromService:
          type: redis
          name: vulcan-redis
          property: connectionString
```

#### 5. Update `agents/core/api.py` - Use cache

Add caching to the `/chat` endpoint:

```python
from .redis_adapter import get_cache

@app.post("/chat")
async def chat(request: ChatRequest):
    cache = get_cache()
    
    # Create cache key from message
    cache_key = f"chat:{request.messages[-1].content}"
    
    # Check cache first
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    # ... existing logic ...
    
    # Cache the response
    response = {"response": response, "agent": agent_type}
    cache.set(cache_key, response, ttl=3600)  # 1 hour
    return response
```

#### 6. Update `REFERENCES.md` - Document Redis

Add to packages table:
```
| redis | 5.0.1 | Cache layer | `pip install redis` |
```

#### 7. Update `task.md` - Track completion

Add under Phase 8 or create Phase 8.5:
```
### Phase 8.5: Performance Optimization
- [x] Redis cache adapter (`agents/core/redis_adapter.py`)
- [x] Docker Redis service
- [x] Render Redis integration
```

---

## 📊 CACHE TTL RECOMMENDATIONS

| Data Type | TTL | Reason |
|-----------|-----|--------|
| LLM responses | 3600s (1hr) | Same question = same answer |
| RAG results | 1800s (30min) | Memory updates occasionally |
| Strategy configs | 300s (5min) | Rarely changes |
| Health checks | 60s (1min) | Don't spam |

---

## ✅ ACCEPTANCE CRITERIA

- [ ] `redis_adapter.py` created (~100-150 lines)
- [ ] Docker compose includes Redis
- [ ] Render.yaml includes Redis
- [ ] Cache used in `/chat` endpoint
- [ ] Health check includes Redis status
- [ ] REFERENCES.md updated
- [ ] task.md updated

---

## 🔗 REFERENCES

- Redis Python docs: https://redis.io/docs/clients/python/
- Render Redis: https://render.com/docs/redis

---

**Delete this file after completing the task.**
