"""
Agents Core Module
Provides shared utilities, orchestrator, health monitoring, auth, and alerts.
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
from .rate_limiter import (
    RateLimiter,
    RateLimitConfig,
    RateLimitExceeded,
    get_rate_limiter,
    rate_limit
)
from .auth_adapter import (
    AuthAdapter,
    AuthConfig,
    TokenPayload,
    AuthError,
    get_auth_adapter,
    require_auth
)
from .alerts_adapter import (
    AlertsAdapter,
    AlertConfig,
    Alert,
    AlertSeverity,
    AlertChannel,
    get_alerts_adapter
)

__all__ = [
    # Logging
    "BlackBoxLogger",
    "get_logger",
    # Orchestrator
    "OrchestratorAdapter",
    "AgentType",
    "TaskRequest",
    "TaskResult",
    "get_orchestrator",
    # Health
    "HealthDashboard",
    "ServiceStatus",
    "DashboardData",
    "get_dashboard",
    # Voice
    "VoiceAdapter",
    "TranscriptionResult",
    "get_voice_adapter",
    # Metrics
    "MetricsViz",
    "ChartData",
    "TimeSeriesPoint",
    "get_metrics_viz",
    # Rate Limiting
    "RateLimiter",
    "RateLimitConfig",
    "RateLimitExceeded",
    "get_rate_limiter",
    "rate_limit",
    # Auth
    "AuthAdapter",
    "AuthConfig",
    "TokenPayload",
    "AuthError",
    "get_auth_adapter",
    "require_auth",
    # Alerts
    "AlertsAdapter",
    "AlertConfig",
    "Alert",
    "AlertSeverity",
    "AlertChannel",
    "get_alerts_adapter",
]
