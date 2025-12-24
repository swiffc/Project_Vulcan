"""
LLM Client Adapter
Unified interface for Claude API with auto-routing and caching.

Integrates:
- Model Router: Haiku for simple, Sonnet for complex
- Redis Cache: Skip API calls for cached responses
- Token Optimizer: Reduce input/output tokens

Packages Used: anthropic (pip install anthropic)
"""

import os
import logging
from typing import List, Dict, Optional, AsyncGenerator
from dataclasses import dataclass

from .model_router import get_model_router, RoutingDecision
from .redis_adapter import get_cache
from .token_optimizer_v2 import get_token_optimizer_v2

logger = logging.getLogger("core.llm")


@dataclass
class LLMResponse:
    """Response from LLM with metadata."""

    content: str
    model: str
    cached: bool
    input_tokens: int
    output_tokens: int
    cost_estimate: float  # USD


class LLMClient:
    """
    Cost-optimized Claude client.

    Usage:
        client = LLMClient()
        response = await client.chat(
            messages=[{"role": "user", "content": "What time is London session?"}],
            agent_type="trading"
        )
        # Uses Haiku (12x cheaper) + caches response
    """

    # Cost per 1M tokens (USD)
    COSTS = {
        "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
        "claude-sonnet-4-20250514": {"input": 3.0, "output": 15.0},
    }

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self._client = None
        self.router = get_model_router()
        self.cache = get_cache()
        self.optimizer = get_token_optimizer()

    @property
    def client(self):
        """Lazy load Anthropic client."""
        if self._client is None:
            import anthropic

            self._client = anthropic.Anthropic(api_key=self.api_key)
        return self._client

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        agent_type: str = "general",
        use_cache: bool = True,
        force_model: str = None,
    ) -> LLMResponse:
        """
        Send chat request with auto-routing and caching.

        Args:
            messages: Conversation history
            system_prompt: System instructions
            agent_type: Agent type for routing decisions
            use_cache: Whether to use cache (default True)
            force_model: Override auto-routing
        """
        # Get last user message for routing
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break

        # Check cache first
        if use_cache:
            cache_key = f"llm:{agent_type}:{user_message[:100]}"
            cached = self.cache.get(cache_key)
            if cached:
                logger.info(f"💾 Cache hit - saved API call")
                return LLMResponse(
                    content=cached["content"],
                    model=cached.get("model", "cached"),
                    cached=True,
                    input_tokens=0,
                    output_tokens=0,
                    cost_estimate=0.0,
                )

        # Route to model
        if force_model:
            routing = RoutingDecision(
                model=force_model,
                max_tokens=4096,
                temperature=0.7,
                complexity="forced",
                reason="Model override",
            )
        else:
            routing = self.router.route(user_message, agent_type)

        logger.info(f"🎯 {routing.reason}")

        # Optimize tokens
        task_type = self.optimizer.get_task_type(user_message, agent_type)
        optimized = self.optimizer.optimize(
            messages=messages,
            system_prompt=system_prompt,
            task_type=task_type,
            complexity=routing.complexity,
        )

        # Build API request
        api_messages = optimized.messages
        if optimized.system_prompt:
            api_messages = [
                {"role": "system", "content": optimized.system_prompt}
            ] + api_messages

        # Call API
        try:
            response = self.client.messages.create(
                model=routing.model,
                max_tokens=min(routing.max_tokens, optimized.max_tokens),
                temperature=routing.temperature,
                messages=api_messages,
            )

            content = response.content[0].text
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            # Calculate cost
            costs = self.COSTS.get(routing.model, self.COSTS["claude-3-haiku-20240307"])
            cost = (
                input_tokens * costs["input"] + output_tokens * costs["output"]
            ) / 1_000_000

            # Cache response
            if use_cache and len(content) < 10000:
                self.cache.set(
                    cache_key, {"content": content, "model": routing.model}, ttl=3600
                )

            return LLMResponse(
                content=content,
                model=routing.model,
                cached=False,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_estimate=cost,
            )

        except Exception as e:
            logger.error(f"LLM error: {e}")
            raise

    async def stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        agent_type: str = "general",
    ) -> AsyncGenerator[str, None]:
        """Stream response for real-time display."""
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break

        routing = self.router.route(user_message, agent_type)

        api_messages = messages
        if system_prompt:
            api_messages = [{"role": "system", "content": system_prompt}] + messages

        with self.client.messages.stream(
            model=routing.model,
            max_tokens=routing.max_tokens,
            temperature=routing.temperature,
            messages=api_messages,
        ) as stream:
            for text in stream.text_stream:
                yield text


# Singleton
_llm: Optional[LLMClient] = None


def get_llm() -> LLMClient:
    global _llm
    if _llm is None:
        _llm = LLMClient()
    return _llm
