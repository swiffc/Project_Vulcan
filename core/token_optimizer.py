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
from typing import List, Dict, Optional
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
    """
    
    # Max tokens by task type
    TOKEN_BUDGETS = {
        "greeting": 128,
        "status_check": 256,
        "simple_query": 256,
        "cad_command": 512,
        "explanation": 1024,
        "trading_query": 1024,
        "trade_review": 2048,
        "audit": 2048,
        "full_analysis": 4096,
        "weekly_review": 4096,
        "default": 1024,
    }
    
    # History limits by complexity
    HISTORY_LIMITS = {
        "simple": 3,
        "moderate": 5,
        "complex": 10,
        "default": 5,
    }
    
    def __init__(self, max_context_tokens: int = 8000):
        self.max_context_tokens = max_context_tokens
        
    def optimize(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        task_type: str = "default",
        complexity: str = "moderate"
    ) -> OptimizedRequest:
        """Optimize request for minimal token usage."""
        original_tokens = self._estimate_tokens(messages, system_prompt)
        
        # Apply optimizations
        trimmed_messages = self._trim_history(messages, complexity)
        compressed_prompt = self._compress_prompt(system_prompt)
        max_tokens = self.TOKEN_BUDGETS.get(task_type, self.TOKEN_BUDGETS["default"])
        
        # Calculate savings
        optimized_tokens = self._estimate_tokens(trimmed_messages, compressed_prompt)
        savings = ((original_tokens - optimized_tokens) / original_tokens * 100) if original_tokens > 0 else 0
        
        if savings > 5:
            logger.info(f"💰 Optimized: {original_tokens} → {optimized_tokens} tokens ({savings:.0f}% saved)")
        
        return OptimizedRequest(
            messages=trimmed_messages,
            system_prompt=compressed_prompt,
            max_tokens=max_tokens,
            estimated_input_tokens=optimized_tokens,
            savings_percent=savings
        )
        
    def _trim_history(self, messages: List[Dict[str, str]], complexity: str) -> List[Dict[str, str]]:
        """Trim conversation to last N messages."""
        limit = self.HISTORY_LIMITS.get(complexity, self.HISTORY_LIMITS["default"])
        
        if len(messages) <= limit:
            return messages
            
        # Keep first (context) + last N-1 messages
        return [messages[0]] + messages[-(limit-1):]
        
    def _compress_prompt(self, prompt: str) -> str:
        """Compress system prompt."""
        if not prompt:
            return prompt
            
        # Remove excessive whitespace
        compressed = re.sub(r'\n{3,}', '\n\n', prompt)
        compressed = re.sub(r' {2,}', ' ', compressed)
        compressed = re.sub(r'-{4,}', '---', compressed)
        
        # Truncate if too long (keep first 2/3 + last 1/3)
        max_chars = 6000
        if len(compressed) > max_chars:
            first = compressed[:int(max_chars * 0.66)]
            last = compressed[-int(max_chars * 0.33):]
            compressed = first + "\n...\n" + last
            
        return compressed.strip()
        
    def _estimate_tokens(self, messages: List[Dict[str, str]], prompt: str) -> int:
        """Estimate tokens (1 token ≈ 4 chars)."""
        total = len(prompt)
        for msg in messages:
            total += len(msg.get("content", ""))
        return total // 4
        
    def get_task_type(self, message: str, agent_type: str = "general") -> str:
        """Infer task type from message."""
        lower = message.lower()
        
        if re.match(r'^(hi|hello|hey|good)', lower):
            return "greeting"
        if any(kw in lower for kw in ["status", "health"]):
            return "status_check"
        if any(kw in lower for kw in ["analyze", "analysis", "comprehensive"]):
            return "full_analysis"
        if "review" in lower:
            return "trade_review" if agent_type == "trading" else "audit"
        if agent_type == "trading":
            return "trading_query"
        if agent_type == "cad":
            return "cad_command"
        if agent_type == "inspector":
            return "audit"
        return "default"
        
    def summarize_context(self, context: str, max_items: int = 3) -> str:
        """Summarize RAG context to top N items."""
        if not context:
            return context
            
        lines = context.strip().split('\n')
        result = []
        item_count = 0
        
        for line in lines:
            if line.startswith('#'):
                result.append(line)
            elif line.strip().startswith(('-', '*', '•')):
                if item_count < max_items:
                    result.append(line)
                    item_count += 1
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
