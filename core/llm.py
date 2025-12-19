"""
Core LLM Client
Wraps the Anthropic API for use by Python agents.
"""

import os
from typing import List, Dict, Optional, Any

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None


class LLMClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            # Try to load from .env file if not in env
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

    def generate(
        self,
        messages: List[Dict[str, str]],
        system: str = "",
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate a response from Claude.
        Args:
            messages: List of {"role": "user"|"assistant", "content": "..."}
            system: System prompt
            model: Model identifier
        """
        if not self.client:
            return "Error: LLM Client not initialized"

        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system,
                messages=messages,
            )
            return response.content[0].text
        except Exception as e:
            return f"Error calling LLM: {str(e)}"


# Global instance
llm = LLMClient()
