"""
Project Vulcan - Core Module

Contains shared functionality used by all agents, including:
- memory: Vector memory and RAG for semantic search
- Cost Optimization: Redis, model routing, token optimization
- Infrastructure Adapters: Orchestrator, health, auth, alerts, etc.
"""

from . import memory
from .logging import BlackBoxLogger, get_logger
from .redis_adapter import RedisCacheAdapter, get_cache
from .model_router import ModelRouter, ModelTier, RoutingDecision, get_model_router
from .token_optimizer_v2 import TokenOptimizerV2, get_token_optimizer_v2
from .orchestrator_adapter import (
    OrchestratorAdapter,
    AgentType,
    TaskRequest,
    TaskResult,
    get_orchestrator,
)
from .health_dashboard import (
    HealthDashboard,
    ServiceStatus,
    DashboardData,
    get_dashboard,
)
from .voice_adapter import VoiceAdapter, TranscriptionResult, get_voice_adapter
from .metrics_viz import MetricsViz, ChartData, TimeSeriesPoint, get_metrics_viz
from .rate_limiter import (
    RateLimiter,
    RateLimitConfig,
    RateLimitExceeded,
    get_rate_limiter,
    rate_limit,
)
from .auth_adapter import (
    AuthAdapter,
    AuthConfig,
    TokenPayload,
    AuthError,
    get_auth_adapter,
    require_auth,
)
from .alerts_adapter import (
    AlertsAdapter,
    AlertConfig,
    Alert,
    AlertSeverity,
    AlertChannel,
    get_alerts_adapter,
)

__all__ = [
    # Memory
    "memory",
    # Logging
    "BlackBoxLogger",
    "get_logger",
    # Cost Optimization Stack
    "RedisCacheAdapter",
    "get_cache",
    "ModelRouter",
    "ModelTier",
    "RoutingDecision",
    "get_model_router",
    "get_model_router",
    "TokenOptimizerV2",
    "get_token_optimizer_v2",
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
