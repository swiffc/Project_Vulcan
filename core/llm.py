"""
Core LLM Client
Wraps the Anthropic API for use by Python agents.

Features:
- Auto model routing (Haiku for simple, Sonnet for complex)
- Token optimization (history trimming, prompt compression)
- Redis caching for repeated queries
"""

import os
import logging
from typing import List, Dict, Optional

logger = logging.getLogger("core.llm")

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None


class LLMClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            try:
                from dotenv import load_dotenv
                load_dotenv()
                self.api_key = os.getenv("ANTHROPIC_API_KEY")
            except ImportError:
                pass

        if self.api_key and Anthropic:
            self.client = Anthropic(api_key=self.api_key)
        else:
            self.client = None
            print("Warning: Anthropic client not initialized (missing key or library)")
            
        # Lazy load optimizers
        self._router = None
        self._optimizer = None
        self._cache = None
        
    @property
    def router(self):
        """Lazy load model router."""
        if self._router is None:
            try:
                from agents.core.model_router import get_model_router
                self._router = get_model_router()
            except ImportError:
                pass
        return self._router
        
    @property
    def optimizer(self):
        """Lazy load token optimizer."""
        if self._optimizer is None:
            try:
                from agents.core.token_optimizer import get_token_optimizer
                self._optimizer = get_token_optimizer()
            except ImportError:
                pass
        return self._optimizer
        
    @property
    def cache(self):
        """Lazy load Redis cache."""
        if self._cache is None:
            try:
                from agents.core.redis_adapter import get_cache
                self._cache = get_cache()
            except ImportError:
                pass
        return self._cache

    def generate(
        self,
        messages: List[Dict[str, str]],
        system: str = "",
        model: str = None,
        max_tokens: int = None,
        temperature: float = None,
        auto_route: bool = True,
        optimize_tokens: bool = True,
        use_cache: bool = True,
        agent_type: str = "general",
    ) -> str:
        """
        Generate a response from Claude with cost optimizations.
        
        Args:
            messages: List of {"role": "user"|"assistant", "content": "..."}
            system: System prompt
            model: Model identifier (auto-selected if None)
            max_tokens: Max response tokens (auto-selected if None)
            temperature: Response temperature
            auto_route: Use model router for cost optimization
            optimize_tokens: Use token optimizer
            use_cache: Check Redis cache first
            agent_type: Agent type for routing decisions
        """
        if not self.client:
            return "Error: LLM Client not initialized"
            
        last_message = messages[-1]["content"] if messages else ""
        
        # 1. Check cache first
        if use_cache and self.cache:
            cache_key = f"llm:{last_message[:100]}:{agent_type}"
            cached = self.cache.get(cache_key)
            if cached:
                logger.info("⚡ Cache HIT - returning cached response")
                return cached
        
        # 2. Auto-route to appropriate model
        if auto_route and model is None and self.router:
            decision = self.router.route(last_message, agent_type)
            model = decision.model
            max_tokens = max_tokens or decision.max_tokens
            temperature = temperature or decision.temperature
            logger.info(f"🎯 Routed: {decision.reason}")
        else:
            model = model or "claude-sonnet-4-20250514"
            max_tokens = max_tokens or 4096
            temperature = temperature or 0.7
            
        # 3. Optimize tokens
        if optimize_tokens and self.optimizer:
            task_type = self.optimizer.get_task_type(last_message, agent_type)
            optimized = self.optimizer.optimize(
                messages=messages,
                system_prompt=system,
                task_type=task_type,
                complexity=self.router.assess_complexity(last_message).value if self.router else "moderate"
            )
            messages = optimized.messages
            system = optimized.system_prompt
            # Don't override max_tokens if already set by router

        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system,
                messages=messages,
            )
            result = response.content[0].text
            
            # 4. Cache the result
            if use_cache and self.cache:
                cache_key = f"llm:{last_message[:100]}:{agent_type}"
                self.cache.set(cache_key, result, ttl=3600)  # 1 hour TTL
                
            return result
            
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return f"Error calling LLM: {str(e)}"
            
    def generate_simple(
        self,
        prompt: str,
        system: str = "",
    ) -> str:
        """Simple generation for one-off queries (always uses Haiku)."""
        return self.generate(
            messages=[{"role": "user", "content": prompt}],
            system=system,
            model="claude-3-haiku-20240307",
            max_tokens=512,
            auto_route=False,
            optimize_tokens=False,
        )


# Global instance
llm = LLMClient()
