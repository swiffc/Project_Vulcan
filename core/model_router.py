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


class ModelTier(Enum):
    HAIKU = "claude-3-haiku-20240307"      # Fast, cheap ($0.25/M)
    SONNET = "claude-sonnet-4-20250514"     # Balanced ($3/M)


class TaskComplexity(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


@dataclass
class RoutingDecision:
    model: str
    max_tokens: int
    temperature: float
    complexity: str
    reason: str


class ModelRouter:
    """
    Routes queries to the most cost-effective model.
    
    Usage:
        router = ModelRouter()
        decision = router.route("What time does London session open?")
        # decision.model = "claude-3-haiku-20240307" (12x cheaper!)
        
        decision = router.route("Analyze GBP/USD for Q2 manipulation with ICT confluence")
        # decision.model = "claude-sonnet-4-20250514" (full power)
    """
    
    # Patterns indicating SIMPLE queries (use Haiku)
    SIMPLE_PATTERNS = [
        r"what time", r"when does", r"when is", r"what day",
        r"^(hi|hello|hey|good morning|good afternoon|good evening)",
        r"^thanks", r"^thank you", r"^ok\b", r"^okay\b",
        r"status", r"health check",
        r"^(is|are|can|do|does|will|should) \w+ ",
        r"list my", r"show me my", r"what are my",
        r"define ", r"what is (a |an |the )?\w+\?*$",
    ]
    
    # Patterns indicating COMPLEX queries (use Sonnet)
    COMPLEX_PATTERNS = [
        r"analyze", r"analysis", r"analyse",
        r"confluence", r"multiple.*(factor|confirmation|signal)",
        r"ict.*(btmm|concept|setup)", r"btmm.*(ict|cycle)",
        r"quarterly.theory", r"manipulation.phase",
        r"step.by.step", r"walk.*through", r"explain.*detail",
        r"comprehensive", r"in.depth", r"thorough",
        r"review.*(trade|performance|week)", r"audit",
        r"grade", r"evaluate", r"assess",
        r"create.*(plan|strategy)", r"build.*(strategy|system)",
        r"compare.*contrast", r"trade.?off",
        r"complex.*(assembly|geometry|part)",
        r"multi.*(part|step|factor)",
    ]
    
    # Keywords that boost complexity score
    COMPLEXITY_BOOSTERS = [
        "why", "how does", "implications", "consequences",
        "relationship between", "optimize", "best approach",
        "recommend", "should i", "trade-off"
    ]
    
    def __init__(self):
        self._simple_re = [re.compile(p, re.IGNORECASE) for p in self.SIMPLE_PATTERNS]
        self._complex_re = [re.compile(p, re.IGNORECASE) for p in self.COMPLEX_PATTERNS]
        
    def assess_complexity(self, message: str) -> TaskComplexity:
        """Assess query complexity."""
        message_lower = message.lower()
        
        # Score patterns
        complex_score = sum(1 for p in self._complex_re if p.search(message))
        simple_score = sum(1 for p in self._simple_re if p.search(message))
        booster_score = sum(1 for kw in self.COMPLEXITY_BOOSTERS if kw in message_lower)
        
        # Length factor
        word_count = len(message.split())
        length_bonus = 1 if word_count > 30 else 0
        
        total_complex = complex_score + booster_score + length_bonus
        
        if total_complex >= 2:
            return TaskComplexity.COMPLEX
        elif simple_score >= 1 and total_complex == 0:
            return TaskComplexity.SIMPLE
        return TaskComplexity.MODERATE
        
    def route(self, message: str, agent_type: str = "general") -> RoutingDecision:
        """Route message to appropriate model."""
        complexity = self.assess_complexity(message)
        
        # Agent overrides
        if agent_type == "inspector":
            complexity = TaskComplexity.COMPLEX  # Audits need full reasoning
            
        if complexity == TaskComplexity.SIMPLE:
            return RoutingDecision(
                model=ModelTier.HAIKU.value,
                max_tokens=512,
                temperature=0.3,
                complexity="simple",
                reason="Simple query → Haiku (12x cheaper)"
            )
        elif complexity == TaskComplexity.COMPLEX:
            return RoutingDecision(
                model=ModelTier.SONNET.value,
                max_tokens=4096,
                temperature=0.7,
                complexity="complex",
                reason="Complex analysis → Sonnet (full power)"
            )
        else:
            return RoutingDecision(
                model=ModelTier.HAIKU.value,
                max_tokens=1024,
                temperature=0.5,
                complexity="moderate",
                reason="Moderate query → Haiku (extended tokens)"
            )


# Singleton
_router: Optional[ModelRouter] = None

def get_model_router() -> ModelRouter:
    global _router
    if _router is None:
        _router = ModelRouter()
    return _router
