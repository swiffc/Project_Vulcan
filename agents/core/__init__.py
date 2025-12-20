"""
Agents Core Module
Provides shared utilities, orchestrator, and health monitoring.
"""

from .logging import BlackBoxLogger, get_logger
from .orchestrator_adapter import (
    OrchestratorAdapter,
    AgentType,
    TaskRequest,
    TaskResult,
    get_orchestrator
)
from .health_dashboard import (
    HealthDashboard,
    ServiceStatus,
    DashboardData,
    get_dashboard
)

__all__ = [
    "BlackBoxLogger",
    "get_logger",
    "OrchestratorAdapter",
    "AgentType",
    "TaskRequest",
    "TaskResult",
    "get_orchestrator",
    "HealthDashboard",
    "ServiceStatus",
    "DashboardData",
    "get_dashboard",
]
