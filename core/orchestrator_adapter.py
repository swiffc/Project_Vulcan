"""
Orchestrator Adapter - CrewAI Task Router

Routes user requests to appropriate agents using CrewAI patterns.
Implements Rule 10: Supervisor Orchestration Pattern.

Agents never communicate directly - all routing through this orchestrator.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("core.orchestrator")


class AgentType(Enum):
    """Available agent types."""

    TRADING = "trading"
    CAD = "cad"
    SKETCH = "sketch"
    WORK = "work"
    INSPECTOR = "inspector"
    SYSTEM = "system"
    GENERAL = "general"


@dataclass
class TaskResult:
    """Result from an agent task execution."""

    agent: AgentType
    success: bool
    output: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class TaskRequest:
    """Request to be routed to an agent."""

    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    preferred_agent: Optional[AgentType] = None
    require_review: bool = False


class OrchestratorAdapter:
    """
    CrewAI-style task router and orchestrator.

    Routes requests to appropriate agents based on:
    1. Explicit agent specification
    2. Keyword detection
    3. Context analysis

    Implements Producer-Reviewer pattern (Rule 11) when required.
    """

    # Keywords for agent detection
    AGENT_KEYWORDS = {
        AgentType.TRADING: [
            "trade",
            "trading",
            "forex",
            "gbp",
            "usd",
            "eur",
            "jpy",
            "setup",
            "bias",
            "ict",
            "btmm",
            "quarterly",
            "stacey",
            "order block",
            "fvg",
            "liquidity",
            "manipulation",
            "tradingview",
            "chart",
            "analysis",
            "journal",
        ],
        AgentType.CAD: [
            "cad",
            "solidworks",
            "inventor",
            "autocad",
            "bentley",
            "part",
            "sketch",
            "extrude",
            "flange",
            "model",
            "3d",
            "drawing",
            "assembly",
            "ecn",
            "revision",
            "pdf",
        ],
        AgentType.SKETCH: [
            "photo",
            "sketch",
            "hand-drawn",
            "napkin",
            "ocr",
            "vision",
            "geometry extraction",
            "image to cad",
            "convert image",
        ],
        AgentType.WORK: [
            "teams",
            "outlook",
            "email",
            "meeting",
            "calendar",
            "j2",
            "tracker",
            "work",
            "job",
            "microsoft",
            "task",
        ],
        AgentType.INSPECTOR: [
            "audit",
            "review",
            "grade",
            "inspect",
            "judge",
            "report",
            "performance",
            "analyze results",
        ],
        AgentType.SYSTEM: [
            "backup",
            "health",
            "status",
            "metrics",
            "schedule",
            "system",
            "maintenance",
            "uptime",
        ],
    }

    def __init__(self):
        self.agents: Dict[AgentType, Any] = {}
        self.task_history: List[TaskResult] = []

    def register_agent(self, agent_type: AgentType, agent_instance: Any) -> None:
        """Register an agent instance for routing."""
        self.agents[agent_type] = agent_instance
        logger.info(f"Registered agent: {agent_type.value}")

    def detect_agent(self, message: str) -> AgentType:
        """
        Detect which agent should handle the request.

        Args:
            message: User message to analyze.

        Returns:
            Best matching AgentType.
        """
        message_lower = message.lower()
        scores = {agent: 0 for agent in AgentType}

        for agent_type, keywords in self.AGENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in message_lower:
                    scores[agent_type] += 1

        # Find highest scoring agent
        best_agent = max(scores, key=scores.get)

        # Default to general if no keywords matched
        if scores[best_agent] == 0:
            return AgentType.GENERAL

        return best_agent

    async def route(self, request: TaskRequest) -> TaskResult:
        """
        Route a task request to the appropriate agent.

        Args:
            request: TaskRequest with message and context.

        Returns:
            TaskResult from the agent execution.
        """
        # Determine agent
        agent_type = request.preferred_agent or self.detect_agent(request.message)
        logger.info(f"Routing to agent: {agent_type.value}")

        # Check if agent is registered
        if agent_type not in self.agents and agent_type != AgentType.GENERAL:
            logger.warning(
                f"Agent {agent_type.value} not registered, " "falling back to general"
            )
            agent_type = AgentType.GENERAL

        # Execute task
        try:
            result = await self._execute_task(agent_type, request)

            # Apply Producer-Reviewer pattern if required
            if request.require_review and result.success:
                result = await self._review_result(result, request)

            self.task_history.append(result)
            return result

        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return TaskResult(
                agent=agent_type, success=False, output=None, error=str(e)
            )

    async def _execute_task(
        self, agent_type: AgentType, request: TaskRequest
    ) -> TaskResult:
        """Execute task on specific agent."""
        agent = self.agents.get(agent_type)

        if agent is None:
            # Check if this is a general request
            if agent_type == AgentType.GENERAL:
                return TaskResult(
                    agent=agent_type,
                    success=True,
                    output=f"Processing general request: {request.message[:100]}",
                )

            return TaskResult(
                agent=agent_type,
                success=False,
                output=None,
                error=f"Agent category '{agent_type.value}' is offline.",
            )

        # Call agent's process method if available
        if hasattr(agent, "process"):
            output = await agent.process(request.message, request.context)
        elif hasattr(agent, "run"):
            output = await agent.run(request.message)
        else:
            output = f"Agent {agent_type.value} has no process/run method"

        return TaskResult(agent=agent_type, success=True, output=output)

    async def _review_result(
        self, result: TaskResult, request: TaskRequest
    ) -> TaskResult:
        """
        Apply Producer-Reviewer pattern (Rule 11).

        Send result to Inspector for validation.
        """
        inspector = self.agents.get(AgentType.INSPECTOR)

        if inspector is None:
            logger.warning("Inspector not available for review")
            result.metadata["reviewed"] = False
            return result

        try:
            review = await inspector.audit(result.output, request.context)
            result.metadata["reviewed"] = True
            result.metadata["review_result"] = review
        except Exception as e:
            logger.error(f"Review failed: {e}")
            result.metadata["reviewed"] = False
            result.metadata["review_error"] = str(e)

        return result

    def get_agent_status(self) -> Dict[str, str]:
        """Get registration status of all agents."""
        return {
            agent.value: "registered" if agent in self.agents else "not_registered"
            for agent in AgentType
        }

    def get_task_history(self, limit: int = 10) -> List[Dict]:
        """Get recent task history."""
        return [
            {"agent": r.agent.value, "success": r.success, "error": r.error}
            for r in self.task_history[-limit:]
        ]


# Singleton instance
_orchestrator: Optional[OrchestratorAdapter] = None


def get_orchestrator() -> OrchestratorAdapter:
    """Get or create orchestrator singleton."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = OrchestratorAdapter()
    return _orchestrator
