"""
Model Router Adapter
Routes queries to appropriate model based on complexity.

Simple tasks → Haiku (12x cheaper)
Complex tasks → Sonnet (full power)

Packages Used: None (pure Python)
"""

import logging
import re
from typing import Optional
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger("core.model-router")


class ModelProvider(str, Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"


class ModelTier(Enum):
    # Engineering / Code Specialist
    SONNET = "claude-3-5-sonnet-20240620"
    # General Reasoning / Finance Specialist
    GPT4O = "gpt-4o"
    # Fast / Cheap
    GPT4O_MINI = "gpt-4o-mini"
    HAIKU = "claude-3-haiku-20240307"


@dataclass
class RoutingDecision:
    provider: ModelProvider
    model: str
    max_tokens: int
    temperature: float
    complexity: str
    reason: str


class ModelRouter:
    """
    Routes queries to the most effective model based on Domain and Complexity.

    Strategies:
    1. CAD/Engineering/Code -> Claude 3.5 Sonnet (Best spatial/coding)
    2. Trading/Finance/Strategy -> GPT-4o (Best general reasoning)
    3. Simple/Chat -> GPT-4o-mini (Cheapest/Fastest)
    """

    # Patterns for Domain Detection
    CAD_PATTERNS = [
        r"cad",
        r"solidworks",
        r"inventor",
        r"model",
        r"geometry",
        r"dimension",
        r"tolerance",
        r"drawing",
        r"part number",
        r"assembly",
        r"bom",
        r"material",
        r"weld",
        r"gdt",
        r"gd&t",
    ]

    TRADING_PATTERNS = [
        r"trade",
        r"finance",
        r"market",
        r"price",
        r"chart",
        r"ict",
        r"fvg",
        r"liquidity",
        r"bias",
        r"trend",
        r"forex",
        r"crypto",
        r"stock",
        r"quarterly",
        r"manipulation",
    ]

    def __init__(self):
        self._cad_re = [re.compile(p, re.IGNORECASE) for p in self.CAD_PATTERNS]
        self._trade_re = [re.compile(p, re.IGNORECASE) for p in self.TRADING_PATTERNS]

    def detect_domain(self, message: str) -> str:
        """Detect domain: 'cad', 'trading', or 'general'."""
        cad_score = sum(1 for p in self._cad_re if p.search(message))
        trade_score = sum(1 for p in self._trade_re if p.search(message))

        if cad_score > trade_score:
            return "cad"
        elif trade_score > cad_score:
            return "trading"
        return "general"

    def route(self, message: str, agent_type: str = "general") -> RoutingDecision:
        """Route message to appropriate model."""
        domain = self.detect_domain(message)

        # Override based on explicit agent type
        if agent_type == "cad_agent":
            return self._route_engineering(message)
        elif agent_type == "trading_agent":
            return self._route_trading(message)

        # Domain-based routing
        if domain == "cad":
            return self._route_engineering(message)
        elif domain == "trading":
            return self._route_trading(message)
        else:
            return self._route_general(message)

    def _route_engineering(self, message: str) -> RoutingDecision:
        """Engineering tasks go to Claude 3.5 Sonnet."""
        return RoutingDecision(
            provider=ModelProvider.ANTHROPIC,
            model=ModelTier.SONNET.value,
            max_tokens=8192,
            temperature=0.2,  # Low temp for precision
            complexity="complex",
            reason="Engineering task → Claude 3.5 Sonnet (Best Spatial/Code)",
        )

    def _route_trading(self, message: str) -> RoutingDecision:
        """Trading logic goes to GPT-4o."""
        return RoutingDecision(
            provider=ModelProvider.OPENAI,
            model=ModelTier.GPT4O.value,
            max_tokens=4096,
            temperature=0.7,
            complexity="complex",
            reason="Trading analysis → GPT-4o (Best General Reasoning)",
        )

    def _route_general(self, message: str) -> RoutingDecision:
        """General chat goes to GPT-4o-mini (unless complex)."""
        # Simple heuristic for complexity
        is_complex = len(message.split()) > 30 or "analyze" in message.lower()

        if is_complex:
            return RoutingDecision(
                provider=ModelProvider.OPENAI,
                model=ModelTier.GPT4O.value,
                max_tokens=2048,
                temperature=0.7,
                complexity="moderate",
                reason="Complex general query → GPT-4o",
            )
        else:
            return RoutingDecision(
                provider=ModelProvider.OPENAI,
                model=ModelTier.GPT4O_MINI.value,
                max_tokens=1024,
                temperature=0.6,
                complexity="simple",
                reason="Simple query → GPT-4o-mini (Cost Optimized)",
            )


# Singleton
_router: Optional[ModelRouter] = None


def get_model_router() -> ModelRouter:
    global _router
    if _router is None:
        _router = ModelRouter()
    return _router
