"""
Black Box Decision Logger (Observability)
Captures structured logs of agent Thought -> Action -> Result cycles.
Stores logs in JSONL format for easy parsing and replay.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import uuid


class BlackBoxLogger:
    def __init__(self, agent_id: str, log_dir: str = "storage/logs/decisions"):
        self.agent_id = agent_id
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Current session ID
        self.session_id = str(uuid.uuid4())
        self.log_file = (
            self.log_dir
            / f"{self.agent_id}_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        )

    def log_decision(
        self,
        trigger: str,
        thought_process: str,
        action: str,
        action_params: Dict[str, Any],
        result: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Log a complete decision cycle."""

        entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "trigger": trigger,  # What caused this cycle (e.g., user message, price alert)
            "thought": thought_process,  # The LLM's reasoning
            "action": action,  # The tool triggered
            "params": action_params,  # Tool arguments
            "result": result,  # Tool output/outcome
            "metadata": metadata or {},
        }

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

        return entry


# Global instance factory
_loggers = {}


def get_logger(agent_id: str) -> BlackBoxLogger:
    if agent_id not in _loggers:
        _loggers[agent_id] = BlackBoxLogger(agent_id)
    return _loggers[agent_id]
