# NEXT TASK 3 FOR CLI

**From**: Claude Chat
**Priority**: High
**Type**: Cost Optimization - Token Optimizer

---

## 📋 TASK: Add Token Optimizer for Cost Reduction

### WHY
- Every token costs money ($3/M input, $15/M output for Sonnet)
- Current setup sends max_tokens=4096 for EVERYTHING
- Full conversation history sent every time
- System prompts are verbose (~500 tokens each)
- **Estimated savings: 20-40% on API costs**

### WHAT TO BUILD

#### 1. Create `agents/core/token_optimizer.py` (~150 lines)

```python
"""
Token Optimizer Adapter
Reduces token usage through smart trimming and compression.

Strategies:
1. Dynamic max_tokens based on task type
2. Conversation history trimming (keep last N)
3. System prompt compression
4. RAG context summarization

Packages Used: None (pure Python)
"""

import logging
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger("core.token-optimizer")


@dataclass
class OptimizedRequest:
    """Optimized request ready for LLM."""
    messages: List[Dict[str, str]]
    system_prompt: str
    max_tokens: int
    estimated_input_tokens: int
    savings_percent: float


class TokenOptimizer:
    """
    Optimizes token usage to reduce API costs.
    
    Usage:
        optimizer = TokenOptimizer()
        optimized = optimizer.optimize(
            messages=conversation_history,
            system_prompt=full_prompt,
            task_type="trading_query"
        )
        # Use optimized.messages, optimized.system_prompt, optimized.max_tokens
    """
    
    # Max tokens by task type
    TOKEN_BUDGETS = {
        # Simple queries need short responses
        "simple_query": 256,
        "greeting": 128,
        "status_check": 256,
        
        # Moderate tasks
        "explanation": 1024,
        "trading_query": 1024,
        "cad_command": 512,
        
        # Complex tasks need full capacity
        "full_analysis": 4096,
        "trade_review": 2048,
        "weekly_review": 4096,
        "audit": 2048,
        
        # Default
        "default": 1024,
    }
    
    # Max conversation history by context
    HISTORY_LIMITS = {
        "simple": 3,      # Last 3 messages for simple queries
        "moderate": 5,    # Last 5 for moderate
        "complex": 10,    # Last 10 for complex analysis
        "default": 5,
    }
    
    def __init__(self, max_context_tokens: int = 8000):
        """
        Args:
            max_context_tokens: Max tokens for entire context (safety limit)
        """
        self.max_context_tokens = max_context_tokens
        
    def optimize(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        task_type: str = "default",
        complexity: str = "moderate"
    ) -> OptimizedRequest:
        """
        Optimize a request for minimal token usage.
        
        Args:
            messages: Full conversation history
            system_prompt: Original system prompt
            task_type: Type of task (for max_tokens budget)
            complexity: Query complexity (for history limit)
            
        Returns:
            OptimizedRequest with trimmed data
        """
        original_tokens = self._estimate_tokens(messages, system_prompt)
        
        # 1. Trim conversation history
        trimmed_messages = self._trim_history(messages, complexity)
        
        # 2. Compress system prompt
        compressed_prompt = self._compress_system_prompt(system_prompt)
        
        # 3. Get appropriate max_tokens
        max_tokens = self.TOKEN_BUDGETS.get(task_type, self.TOKEN_BUDGETS["default"])
        
        # Calculate savings
        optimized_tokens = self._estimate_tokens(trimmed_messages, compressed_prompt)
        savings = ((original_tokens - optimized_tokens) / original_tokens * 100) if original_tokens > 0 else 0
        
        logger.info(f"💰 Token optimization: {original_tokens} → {optimized_tokens} ({savings:.1f}% saved)")
        
        return OptimizedRequest(
            messages=trimmed_messages,
            system_prompt=compressed_prompt,
            max_tokens=max_tokens,
            estimated_input_tokens=optimized_tokens,
            savings_percent=savings
        )
        
    def _trim_history(
        self, 
        messages: List[Dict[str, str]], 
        complexity: str
    ) -> List[Dict[str, str]]:
        """Trim conversation history to last N messages."""
        limit = self.HISTORY_LIMITS.get(complexity, self.HISTORY_LIMITS["default"])
        
        if len(messages) <= limit:
            return messages
            
        # Always keep the first message (often contains important context)
        # and the last N-1 messages
        if len(messages) > limit:
            trimmed = [messages[0]] + messages[-(limit-1):]
            logger.debug(f"Trimmed history: {len(messages)} → {len(trimmed)} messages")
            return trimmed
            
        return messages
        
    def _compress_system_prompt(self, prompt: str) -> str:
        """Compress system prompt by removing redundancy."""
        if not prompt:
            return prompt
            
        compressed = prompt
        
        # Remove excessive whitespace
        compressed = re.sub(r'\n{3,}', '\n\n', compressed)
        compressed = re.sub(r' {2,}', ' ', compressed)
        
        # Remove markdown formatting that's not essential
        # (Keep headers and bullets, remove excessive decoration)
        compressed = re.sub(r'\*{3,}', '**', compressed)
        compressed = re.sub(r'-{3,}', '---', compressed)
        
        # Truncate if still too long (keep first and last parts)
        max_prompt_tokens = 1500  # ~6000 chars
        max_chars = max_prompt_tokens * 4
        
        if len(compressed) > max_chars:
            # Keep first 2/3 and last 1/3
            first_part = compressed[:int(max_chars * 0.66)]
            last_part = compressed[-int(max_chars * 0.33):]
            compressed = first_part + "\n\n[...condensed...]\n\n" + last_part
            logger.debug(f"Compressed prompt: {len(prompt)} → {len(compressed)} chars")
            
        return compressed.strip()
        
    def _estimate_tokens(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: str
    ) -> int:
        """Estimate token count (rough: 1 token ≈ 4 chars)."""
        total_chars = len(system_prompt)
        for msg in messages:
            total_chars += len(msg.get("content", ""))
        return total_chars // 4
        
    def get_task_type(self, message: str, agent_type: str) -> str:
        """Infer task type from message content."""
        lower = message.lower()
        
        # Greetings
        if re.match(r'^(hi|hello|hey|good)', lower):
            return "greeting"
            
        # Status checks
        if any(kw in lower for kw in ["status", "health", "check"]):
            return "status_check"
            
        # Full analysis
        if any(kw in lower for kw in ["analyze", "analysis", "full", "comprehensive", "detailed"]):
            return "full_analysis"
            
        # Reviews
        if "review" in lower:
            return "trade_review" if agent_type == "trading" else "audit"
            
        # Agent-specific defaults
        if agent_type == "trading":
            return "trading_query"
        elif agent_type == "cad":
            return "cad_command"
        elif agent_type == "inspector":
            return "audit"
            
        return "default"
        
    def summarize_rag_context(self, context: str, max_items: int = 3) -> str:
        """Summarize RAG context to reduce tokens."""
        if not context:
            return context
            
        lines = context.strip().split('\n')
        
        # Keep headers and first N items
        result = []
        item_count = 0
        
        for line in lines:
            # Keep headers
            if line.startswith('#'):
                result.append(line)
            # Keep items up to limit
            elif line.strip().startswith(('-', '*', '•')) or line.strip()[0:2].isdigit():
                if item_count < max_items:
                    result.append(line)
                    item_count += 1
            # Keep short lines (metadata)
            elif len(line) < 50:
                result.append(line)
                
        return '\n'.join(result)


# Singleton
_optimizer: Optional[TokenOptimizer] = None

def get_token_optimizer() -> TokenOptimizer:
    global _optimizer
    if _optimizer is None:
        _optimizer = TokenOptimizer()
    return _optimizer
```

#### 2. Update `core/llm.py` - Integrate optimizer

```python
from agents.core.token_optimizer import get_token_optimizer

class LLMClient:
    def __init__(self, api_key: Optional[str] = None):
        # ... existing init ...
        self.optimizer = get_token_optimizer()
        
    def generate(
        self,
        messages: List[Dict[str, str]],
        system: str = "",
        model: str = None,
        max_tokens: int = None,
        temperature: float = None,
        auto_route: bool = True,
        optimize_tokens: bool = True,  # NEW
        task_type: str = "default",     # NEW
    ) -> str:
        """Generate with optional token optimization."""
        
        # Optimize tokens if enabled
        if optimize_tokens:
            optimized = self.optimizer.optimize(
                messages=messages,
                system_prompt=system,
                task_type=task_type,
                complexity="moderate"  # Could also be routed
            )
            messages = optimized.messages
            system = optimized.system_prompt
            max_tokens = max_tokens or optimized.max_tokens
            
        # ... rest of existing code ...
```

#### 3. Update `apps/web/src/lib/claude-client.ts` - Add trimming

```typescript
// Add helper function
function trimConversationHistory(
  messages: ChatMessage[], 
  maxMessages: number = 5
): ChatMessage[] {
  if (messages.length <= maxMessages) {
    return messages;
  }
  
  // Keep first message (context) + last N-1
  const first = messages[0];
  const recent = messages.slice(-(maxMessages - 1));
  
  console.log(`[TokenOptimizer] Trimmed ${messages.length} → ${maxMessages} messages`);
  return [first, ...recent];
}

// Add token budget helper
function getMaxTokens(message: string): number {
  const lower = message.toLowerCase();
  
  if (/^(hi|hello|hey)/.test(lower)) return 128;
  if (/status|health|check/.test(lower)) return 256;
  if (/analyze|analysis|comprehensive/.test(lower)) return 4096;
  if (/review|audit/.test(lower)) return 2048;
  
  return 1024; // Default
}

// Update streamChat
export async function streamChat(
  messages: ChatMessage[],
  systemPrompt: string,
  callbacks: StreamCallbacks
): Promise<void> {
  // Trim history
  const trimmedMessages = trimConversationHistory(messages, 5);
  
  // Get appropriate token budget
  const lastMessage = messages[messages.length - 1]?.content || "";
  const maxTokens = getMaxTokens(lastMessage);
  
  // ... use trimmedMessages and maxTokens in API call ...
}
```

#### 4. Update `agents/core/api.py` - Add optimization

```python
from .token_optimizer import get_token_optimizer

@app.post("/chat")
async def chat(request: ChatRequest):
    # ... existing code ...
    
    # Optimize before sending to LLM
    optimizer = get_token_optimizer()
    task_type = optimizer.get_task_type(last_message, agent_type)
    
    optimized = optimizer.optimize(
        messages=[{"role": m.role, "content": m.content} for m in request.messages],
        system_prompt=system_prompt,
        task_type=task_type
    )
    
    # Use optimized values
    response = llm.generate(
        messages=optimized.messages,
        system=optimized.system_prompt,
        max_tokens=optimized.max_tokens
    )
    
    # ... rest of code ...
```

#### 5. Update `REFERENCES.md`

Add to Cost Optimization section:
```markdown
| Token Optimizer | `agents/core/token_optimizer.py` | 20-40% |
| History trimming | Keep last 5 messages | Reduces context |
| Dynamic max_tokens | 128-4096 based on task | Reduces output waste |
```

#### 6. Update `task.md`

Add to Phase 8.5:
```markdown
- [x] Token optimizer adapter (`agents/core/token_optimizer.py`)
- [x] Conversation history trimming
- [x] Dynamic max_tokens budgets
- [x] System prompt compression
```

---

## 📊 TOKEN BUDGET REFERENCE

| Task Type | max_tokens | Use Case |
|-----------|------------|----------|
| greeting | 128 | "Hi", "Hello" |
| status_check | 256 | "What's the status?" |
| simple_query | 256 | "What time does X?" |
| cad_command | 512 | "Extrude this sketch" |
| trading_query | 1024 | "What's my bias today?" |
| explanation | 1024 | "Explain order blocks" |
| trade_review | 2048 | "Review my last trade" |
| audit | 2048 | "Audit this CAD job" |
| full_analysis | 4096 | "Full Q2 analysis" |
| weekly_review | 4096 | "Weekly performance" |

---

## ✅ ACCEPTANCE CRITERIA

- [ ] `agents/core/token_optimizer.py` created (~150 lines)
- [ ] `core/llm.py` updated with optimize_tokens parameter
- [ ] `claude-client.ts` updated with trimConversationHistory
- [ ] `agents/core/api.py` uses optimizer
- [ ] Conversation history limited to last 5 messages
- [ ] max_tokens varies by task type
- [ ] Logging shows token savings
- [ ] REFERENCES.md updated
- [ ] task.md updated

---

## 💰 EXPECTED SAVINGS

| Optimization | Before | After | Savings |
|--------------|--------|-------|---------|
| Avg max_tokens | 4096 | ~1000 | 75% output buffer |
| History messages | All | Last 5 | ~60% context |
| System prompt | ~500 tokens | ~300 tokens | 40% |
| **Combined** | | | **20-40% cost reduction** |

---

**Delete this file after completing the task.**
