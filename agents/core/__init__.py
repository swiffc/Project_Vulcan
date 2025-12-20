"""
Agents Core Module
Provides shared utilities, orchestrator, health monitoring, and input adapters.
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
from .voice_adapter import (
    VoiceAdapter,
    TranscriptionResult,
    get_voice_adapter
)
from .metrics_viz import (
    MetricsViz,
    ChartData,
    TimeSeriesPoint,
    get_metrics_viz
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
    "VoiceAdapter",
    "TranscriptionResult",
    "get_voice_adapter",
    "MetricsViz",
    "ChartData",
    "TimeSeriesPoint",
    "get_metrics_viz",
]
