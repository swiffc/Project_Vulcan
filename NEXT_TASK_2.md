# NEXT TASK 2 FOR CLI

**From**: Claude Chat
**Priority**: High
**Type**: Cost Optimization - Tiered Model Routing

---

## 📋 TASK: Add Model Router for Cost Optimization

### WHY
- Sonnet costs $3/M input, $15/M output
- Haiku costs $0.25/M input, $1.25/M output (12x cheaper!)
- 50%+ of queries are simple and don't need Sonnet
- **Estimated savings: 50-70% on API costs**

### WHAT TO BUILD

#### 1. Create `agents/core/model_router.py` (~120 lines)

```python
"""
Model Router Adapter
Routes queries to appropriate model based on complexity.

Simple tasks → Haiku (12x cheaper)
Complex tasks → Sonnet (full power)

Packages Used: None (pure Python)
"""

import logging
import re
from typing import Tuple, Optional
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger("core.model-router")


class ModelTier(Enum):
    HAIKU = "claude-3-haiku-20240307"      # Fast, cheap ($0.25/M)
    SONNET = "claude-sonnet-4-20250514"     # Balanced ($3/M)
    # OPUS for future if needed


class TaskComplexity(Enum):
    SIMPLE = "simple"       # Factual, short answers
    MODERATE = "moderate"   # Some reasoning needed
    COMPLEX = "complex"     # Deep analysis, multi-step


@dataclass
class RoutingDecision:
    model: str
    max_tokens: int
    temperature: float
    reason: str


class ModelRouter:
    """
    Routes queries to the most cost-effective model.
    
    Usage:
        router = ModelRouter()
        decision = router.route("What time does London session open?")
        # decision.model = "claude-3-haiku-20240307"
        # decision.max_tokens = 256
        
        decision = router.route("Analyze GBP/USD for Q2 manipulation setup with ICT confluence")
        # decision.model = "claude-sonnet-4-20250514"
        # decision.max_tokens = 2048
    """
    
    # Patterns that indicate SIMPLE queries (use Haiku)
    SIMPLE_PATTERNS = [
        # Time/schedule questions
        r"what time",
        r"when does",
        r"when is",
        r"what day",
        r"what date",
        
        # Simple factual
        r"what is (a |an |the )?(\w+)$",  # "What is an order block?"
        r"define ",
        r"meaning of",
        r"explain briefly",
        
        # Yes/no questions
        r"^(is|are|can|do|does|will|should) ",
        
        # Status checks
        r"status",
        r"health",
        r"check",
        
        # Simple commands
        r"list ",
        r"show me",
        r"what are my",
        
        # Greetings
        r"^(hi|hello|hey|good morning|good afternoon)",
        r"^thanks",
        r"^thank you",
    ]
    
    # Patterns that indicate COMPLEX queries (use Sonnet)
    COMPLEX_PATTERNS = [
        # Multi-factor analysis
        r"analyze",
        r"analysis",
        r"confluence",
        r"multiple",
        
        # Trading strategy
        r"setup.*with",
        r"ict.*btmm",
        r"quarterly.*theory",
        r"manipulation.*phase",
        
        # Detailed explanation
        r"explain.*detail",
        r"step.by.step",
        r"walk.*through",
        r"comprehensive",
        
        # Review/judgment
        r"review.*trade",
        r"audit",
        r"grade",
        r"evaluate",
        
        # Planning
        r"create.*plan",
        r"build.*strategy",
        r"develop",
        
        # CAD complex
        r"assembly",
        r"multi.*part",
        r"complex.*geometry",
    ]
    
    # Keywords that boost complexity
    COMPLEXITY_BOOSTERS = [
        "why", "how", "compare", "contrast", "relationship",
        "implications", "consequences", "trade-off", "optimize",
        "best approach", "recommend", "strategy"
    ]
    
    def __init__(self):
        self._compile_patterns()
        
    def _compile_patterns(self):
        """Pre-compile regex patterns for performance."""
        self._simple_re = [re.compile(p, re.IGNORECASE) for p in self.SIMPLE_PATTERNS]
        self._complex_re = [re.compile(p, re.IGNORECASE) for p in self.COMPLEX_PATTERNS]
        
    def assess_complexity(self, message: str) -> TaskComplexity:
        """Assess the complexity of a query."""
        message_lower = message.lower()
        
        # Check for complex patterns first (they take priority)
        complex_score = sum(1 for p in self._complex_re if p.search(message))
        
        # Check for simple patterns
        simple_score = sum(1 for p in self._simple_re if p.search(message))
        
        # Check complexity boosters
        booster_score = sum(1 for kw in self.COMPLEXITY_BOOSTERS if kw in message_lower)
        
        # Length factor (longer queries tend to be more complex)
        word_count = len(message.split())
        length_factor = 1 if word_count > 30 else 0
        
        # Calculate final complexity
        total_complex = complex_score + booster_score + length_factor
        
        if total_complex >= 2:
            return TaskComplexity.COMPLEX
        elif simple_score >= 1 and total_complex == 0:
            return TaskComplexity.SIMPLE
        else:
            return TaskComplexity.MODERATE
            
    def route(self, message: str, agent_type: str = "general") -> RoutingDecision:
        """
        Route a message to the appropriate model.
        
        Args:
            message: User's message
            agent_type: Type of agent handling this (trading, cad, general)
            
        Returns:
            RoutingDecision with model, max_tokens, temperature
        """
        complexity = self.assess_complexity(message)
        
        # Agent-specific overrides
        if agent_type == "inspector":
            # Audits always need full reasoning
            complexity = TaskComplexity.COMPLEX
            
        if complexity == TaskComplexity.SIMPLE:
            decision = RoutingDecision(
                model=ModelTier.HAIKU.value,
                max_tokens=512,
                temperature=0.3,
                reason="Simple query - using Haiku for cost efficiency"
            )
        elif complexity == TaskComplexity.COMPLEX:
            decision = RoutingDecision(
                model=ModelTier.SONNET.value,
                max_tokens=4096,
                temperature=0.7,
                reason="Complex analysis - using Sonnet for quality"
            )
        else:  # MODERATE
            decision = RoutingDecision(
                model=ModelTier.HAIKU.value,  # Default to cheaper
                max_tokens=1024,
                temperature=0.5,
                reason="Moderate complexity - using Haiku with extended tokens"
            )
            
        logger.info(f"🎯 Routed to {decision.model.split('-')[1]}: {decision.reason}")
        return decision
        
    def get_stats(self) -> dict:
        """Get routing statistics (for monitoring)."""
        # Would track actual usage in production
        return {
            "simple_pattern_count": len(self.SIMPLE_PATTERNS),
            "complex_pattern_count": len(self.COMPLEX_PATTERNS),
        }


# Singleton
_router: Optional[ModelRouter] = None

def get_model_router() -> ModelRouter:
    global _router
    if _router is None:
        _router = ModelRouter()
    return _router
```

#### 2. Update `core/llm.py` - Use the router

Add router integration:

```python
from agents.core.model_router import get_model_router, RoutingDecision

class LLMClient:
    def __init__(self, api_key: Optional[str] = None):
        # ... existing init ...
        self.router = get_model_router()
        
    def generate(
        self,
        messages: List[Dict[str, str]],
        system: str = "",
        model: str = None,  # Now optional - router decides
        max_tokens: int = None,
        temperature: float = None,
        auto_route: bool = True,  # NEW: Enable smart routing
    ) -> str:
        """Generate with optional auto-routing."""
        
        # Auto-route if enabled and no model specified
        if auto_route and model is None:
            last_message = messages[-1]["content"] if messages else ""
            decision = self.router.route(last_message)
            model = decision.model
            max_tokens = max_tokens or decision.max_tokens
            temperature = temperature or decision.temperature
        else:
            # Defaults
            model = model or "claude-sonnet-4-20250514"
            max_tokens = max_tokens or 4096
            temperature = temperature or 0.7
            
        # ... rest of existing generate code ...
```

#### 3. Update `apps/web/src/lib/claude-client.ts` - Add routing

```typescript
// Add at top of file
interface RoutingDecision {
  model: string;
  maxTokens: number;
  temperature: number;
}

function routeQuery(message: string): RoutingDecision {
  const lowerMessage = message.toLowerCase();
  
  // Simple patterns (use Haiku)
  const simplePatterns = [
    /what time/i,
    /when does/i,
    /^(hi|hello|hey)/i,
    /^thanks/i,
    /status/i,
    /^(is|are|can|do|does) /i,
  ];
  
  // Complex patterns (use Sonnet)
  const complexPatterns = [
    /analyze/i,
    /confluence/i,
    /step.by.step/i,
    /review.*trade/i,
    /audit/i,
    /ict.*btmm/i,
  ];
  
  const isSimple = simplePatterns.some(p => p.test(message));
  const isComplex = complexPatterns.some(p => p.test(message));
  
  if (isComplex) {
    return {
      model: "claude-sonnet-4-20250514",
      maxTokens: 4096,
      temperature: 0.7,
    };
  } else if (isSimple) {
    return {
      model: "claude-3-haiku-20240307",
      maxTokens: 512,
      temperature: 0.3,
    };
  } else {
    // Moderate - use Haiku with more tokens
    return {
      model: "claude-3-haiku-20240307",
      maxTokens: 1024,
      temperature: 0.5,
    };
  }
}

// Update streamChat to use routing
export async function streamChat(
  messages: ChatMessage[],
  systemPrompt: string,
  callbacks: StreamCallbacks
): Promise<void> {
  const lastMessage = messages[messages.length - 1]?.content || "";
  const routing = routeQuery(lastMessage);
  
  console.log(`[ModelRouter] Using ${routing.model} (${routing.maxTokens} tokens)`);
  
  try {
    const stream = await anthropic.messages.stream({
      model: routing.model,  // Dynamic model selection
      max_tokens: routing.maxTokens,
      system: systemPrompt,
      messages: messages.map((m) => ({
        role: m.role,
        content: m.content,
      })),
    });
    // ... rest unchanged ...
```

#### 4. Update `REFERENCES.md`

Add to documentation:
```markdown
## Cost Optimization

| Strategy | Implementation | Savings |
|----------|----------------|---------|
| Model Router | `agents/core/model_router.py` | 50-70% |
| Simple queries → Haiku | Automatic | 12x cheaper |
| Complex queries → Sonnet | Automatic | Full quality |
```

#### 5. Update `task.md`

Add to completed:
```markdown
### Phase 8.5: Cost Optimization
- [x] Model Router adapter (`agents/core/model_router.py`)
- [x] TypeScript router in claude-client.ts
- [x] Auto-routing in LLMClient
```

---

## 📊 ROUTING EXAMPLES

| Query | Complexity | Model | Tokens |
|-------|------------|-------|--------|
| "Hi, what time does London open?" | SIMPLE | Haiku | 512 |
| "What is an order block?" | SIMPLE | Haiku | 512 |
| "Show me my recent trades" | SIMPLE | Haiku | 512 |
| "Analyze GBP/USD for Q2 setup" | COMPLEX | Sonnet | 4096 |
| "Review my trade with ICT confluence" | COMPLEX | Sonnet | 4096 |
| "Explain the BTMM three-day cycle" | MODERATE | Haiku | 1024 |

---

## ✅ ACCEPTANCE CRITERIA

- [ ] `agents/core/model_router.py` created (~120 lines)
- [ ] `core/llm.py` updated with auto_route parameter
- [ ] `claude-client.ts` updated with routeQuery function
- [ ] Simple queries use Haiku
- [ ] Complex queries use Sonnet
- [ ] Logging shows which model was selected
- [ ] REFERENCES.md updated
- [ ] task.md updated

---

**Delete this file after completing the task.**
