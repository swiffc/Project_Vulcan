"""
Core LLM Client - ULTIMATE COST OPTIMIZED
Wraps the Anthropic API with ALL cost-saving features.

Features:
1. Anthropic Native Prompt Caching (90% savings on system prompts)
2. Model Router (Haiku for simple, Sonnet for complex)
3. Token Optimizer (history trimming, prompt compression)
4. Redis Response Caching (avoid duplicate API calls)
5. Batch API support (50% savings for non-urgent)
"""

import os
import logging
from typing import List, Dict, Optional, Any

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
            print("Warning: Anthropic client not initialized")

        # Lazy load optimizers
        self._router = None
        self._optimizer = None
        self._cache = None

    @property
    def router(self):
        if self._router is None:
            try:
                from .model_router import get_model_router

                self._router = get_model_router()
            except ImportError:
                pass
        return self._router

    @property
    def optimizer(self):
        if self._optimizer is None:
            try:
                # Use V2 optimizer with Anthropic native caching
                from .token_optimizer_v2 import get_token_optimizer_v2

                self._optimizer = get_token_optimizer_v2()
            except ImportError:
                print("Warning: TokenOptimizerV2 not found")
        return self._optimizer

    @property
    def cache(self):
        if self._cache is None:
            try:
                from .redis_adapter import get_cache

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
        use_prompt_cache: bool = True,  # NEW: Anthropic native caching
        agent_type: str = "general",
    ) -> str:
        """
        Generate with MAXIMUM cost optimization.

        Cost-saving features:
        1. Redis cache check (avoid duplicate calls entirely)
        2. Model routing (Haiku is 12x cheaper than Sonnet)
        3. Token optimization (reduce input/output tokens)
        4. Anthropic prompt caching (90% cheaper on system prompts)

        Args:
            messages: Conversation history
            system: System prompt
            model: Model (auto-selected if None)
            max_tokens: Max output tokens (auto-selected if None)
            temperature: Response temperature
            auto_route: Use model router
            optimize_tokens: Use token optimizer
            use_cache: Check Redis cache first
            use_prompt_cache: Use Anthropic's native prompt caching
            agent_type: Agent type for routing
        """
        if not self.client:
            return "Error: LLM Client not initialized"

        last_message = messages[-1]["content"] if messages else ""

        # 1. Check Redis cache first (completely free if hit!)
        cache_key = None
        if use_cache and self.cache:
            cache_key = f"llm:{hash(last_message + system + agent_type)}"
            cached = self.cache.get(cache_key)
            if cached:
                logger.info("⚡ Redis cache HIT - FREE response!")
                return cached

        # 2. Route to appropriate model
        if auto_route and model is None and self.router:
            decision = self.router.route(last_message, agent_type)
            model = decision.model
            max_tokens = max_tokens or decision.max_tokens
            temperature = temperature or decision.temperature
            logger.info(f"🎯 Model: {decision.reason}")
        else:
            model = model or "claude-sonnet-4-20250514"
            max_tokens = max_tokens or 4096
            temperature = temperature or 0.7

        # 3. Optimize tokens with V2 (includes Anthropic prompt caching)
        system_payload = system  # Default: plain string

        if optimize_tokens and self.optimizer:
            task_type = self.optimizer.get_task_type(last_message, agent_type)
            complexity = (
                self.optimizer.get_complexity(last_message)
                if hasattr(self.optimizer, "get_complexity")
                else "moderate"
            )

            optimized = self.optimizer.optimize(
                messages=messages,
                system_prompt=system,
                task_type=task_type,
                complexity=complexity,
                enable_cache=use_prompt_cache,
                model=model,
            )

            messages = optimized.messages
            max_tokens = optimized.max_tokens

            # Use structured system with cache_control
            if hasattr(optimized, "system") and optimized.system:
                system_payload = optimized.system
                if optimized.cache_enabled:
                    logger.info(
                        "🔥 Anthropic prompt caching ENABLED (90% savings on system prompt)"
                    )

        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_payload,
                messages=messages,
            )

            result = response.content[0].text

            # Log cache performance if available
            usage = response.usage
            if hasattr(usage, "cache_read_input_tokens"):
                cache_read = getattr(usage, "cache_read_input_tokens", 0)
                cache_create = getattr(usage, "cache_creation_input_tokens", 0)
                if cache_read > 0:
                    logger.info(f"💰 Prompt cache HIT: {cache_read} tokens at 90% off!")
                elif cache_create > 0:
                    logger.info(
                        f"📝 Prompt cache CREATED: {cache_create} tokens (next call = 90% off)"
                    )

            # 4. Store in Redis cache for future
            if use_cache and self.cache and cache_key:
                self.cache.set(cache_key, result, ttl=3600)

            return result

        except Exception as e:
            logger.error(f"LLM error: {e}")
            return f"Error calling LLM: {str(e)}"

    def generate_simple(self, prompt: str, system: str = "") -> str:
        """Quick generation using Haiku (cheapest model)."""
        return self.generate(
            messages=[{"role": "user", "content": prompt}],
            system=system,
            model="claude-3-haiku-20240307",
            max_tokens=512,
            auto_route=False,
            optimize_tokens=False,
            use_prompt_cache=False,
        )

    def generate_batch(
        self, requests: List[Dict[str, Any]], wait_for_completion: bool = True
    ) -> List[str]:
        """
        Batch API for non-urgent tasks (50% cheaper!).

        Args:
            requests: List of {"messages": [...], "system": "..."}
            wait_for_completion: Wait for all results

        Returns:
            List of responses
        """
        if not self.client:
            return ["Error: LLM not initialized"] * len(requests)

        try:
            # Prepare batch
            batch_requests = []
            for i, req in enumerate(requests):
                batch_requests.append(
                    {
                        "custom_id": f"req_{i}",
                        "params": {
                            "model": "claude-sonnet-4-20250514",
                            "max_tokens": 1024,
                            "messages": req.get("messages", []),
                            "system": req.get("system", ""),
                        },
                    }
                )

            # Submit batch
            batch = self.client.messages.batches.create(requests=batch_requests)

            if not wait_for_completion:
                return [f"Batch submitted: {batch.id}"]

            # Poll for completion
            import time

            while batch.processing_status == "in_progress":
                time.sleep(5)
                batch = self.client.messages.batches.retrieve(batch.id)

            # Collect results
            results = []
            for result in self.client.messages.batches.results(batch.id):
                if result.result.type == "succeeded":
                    results.append(result.result.message.content[0].text)
                else:
                    results.append(f"Error: {result.result.error}")

            logger.info(f"📦 Batch complete: {len(results)} results at 50% off!")
            return results

        except Exception as e:
            logger.error(f"Batch error: {e}")
            return [f"Batch error: {e}"] * len(requests)


# Global instance
llm = LLMClient()
