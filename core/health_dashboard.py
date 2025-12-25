"""
Health Dashboard - System Status API

Provides unified health status across all Vulcan services.
Used by web UI dashboard and monitoring.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from core.desktop_client import get_desktop_client

logger = logging.getLogger("core.health_dashboard")


@dataclass
class ServiceStatus:
    """Status of a single service."""
    name: str
    status: str  # "healthy", "degraded", "unhealthy", "unknown"
    latency_ms: Optional[float] = None
    last_check: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DashboardData:
    """Complete dashboard data."""
    timestamp: str
    overall_status: str
    services: List[ServiceStatus]
    agents: Dict[str, str]
    recent_tasks: List[Dict]
    metrics: Dict[str, Any]


class HealthDashboard:
    """
    Unified health dashboard for all Vulcan services.

    Aggregates status from:
    - Orchestrator API
    - Desktop MCP Server
    - Memory Brain
    - Individual agents
    """

    def __init__(self):
        self.services: Dict[str, ServiceStatus] = {}
        self.check_history: List[Dict] = []

        # Service URLs from environment
        self.service_urls = {
            "orchestrator": os.getenv("ORCHESTRATOR_URL", "http://localhost:8000"),
            "desktop": os.getenv("DESKTOP_SERVER_URL", "http://localhost:8765"),
            "memory": os.getenv("MEMORY_SERVER_URL", "http://localhost:8770"),
            "web": os.getenv("WEB_URL", "http://localhost:3000"),
        }

    async def check_all(self) -> DashboardData:
        """
        Run health checks on all services and return dashboard data.

        Returns:
            DashboardData with complete system status.
        """
        timestamp = datetime.utcnow().isoformat()
        services = []

        # Check each service
        for name, url in self.service_urls.items():
            status = await self._check_service(name, url)
            services.append(status)
            self.services[name] = status

        # Get orchestrator data
        agents = await self._get_agent_status()
        recent_tasks = await self._get_recent_tasks()
        metrics = await self._get_metrics()

        # Calculate overall status
        overall = self._calculate_overall_status(services)

        # Store in history
        self.check_history.append({
            "timestamp": timestamp,
            "overall": overall,
            "services": {s.name: s.status for s in services}
        })

        # Keep last 100 checks
        if len(self.check_history) > 100:
            self.check_history = self.check_history[-100:]

        return DashboardData(
            timestamp=timestamp,
            overall_status=overall,
            services=services,
            agents=agents,
            recent_tasks=recent_tasks,
            metrics=metrics
        )

    async def _check_service(self, name: str, url: str) -> ServiceStatus:
        """Check health of a single service."""
        try:
            # Use desktop client for desktop server
            if name == "desktop":
                client = get_desktop_client()
                start = datetime.utcnow()
                result = await client.health_check()
                latency = (datetime.utcnow() - start).total_seconds() * 1000
                
                if result.get("status") == "healthy":
                    return ServiceStatus(
                        name=name,
                        status="healthy",
                        latency_ms=round(latency, 2),
                        last_check=datetime.utcnow().isoformat(),
                        details=result
                    )
                else:
                    return ServiceStatus(
                        name=name,
                        status="unhealthy",
                        last_check=datetime.utcnow().isoformat(),
                        details=result
                    )
            
            # For other services, use HTTP check
            import httpx
            start = datetime.utcnow()

            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{url}/health")
                latency = (datetime.utcnow() - start).total_seconds() * 1000

                if resp.status_code == 200:
                    return ServiceStatus(
                        name=name,
                        status="healthy",
                        latency_ms=round(latency, 2),
                        last_check=datetime.utcnow().isoformat(),
                        details=resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
                    )
                else:
                    return ServiceStatus(
                        name=name,
                        status="degraded",
                        latency_ms=round(latency, 2),
                        last_check=datetime.utcnow().isoformat(),
                        details={"status_code": resp.status_code}
                    )

        except Exception as e:
            return ServiceStatus(
                name=name,
                status="unhealthy",
                last_check=datetime.utcnow().isoformat(),
                details={"error": str(e)}
            )

    async def _get_agent_status(self) -> Dict[str, str]:
        """Get status of registered agents from orchestrator."""
        try:
            from .orchestrator_adapter import get_orchestrator
            orch = get_orchestrator()
            return orch.get_agent_status()
        except Exception:
            return {"error": "orchestrator_unavailable"}

    async def _get_recent_tasks(self) -> List[Dict]:
        """Get recent task history from orchestrator."""
        try:
            from .orchestrator_adapter import get_orchestrator
            orch = get_orchestrator()
            return orch.get_task_history(limit=10)
        except Exception:
            return []

    async def _get_metrics(self) -> Dict[str, Any]:
        """Get system metrics summary."""
        return {
            "uptime_hours": self._calculate_uptime(),
            "checks_performed": len(self.check_history),
            "services_monitored": len(self.service_urls),
        }

    def _calculate_overall_status(self, services: List[ServiceStatus]) -> str:
        """Calculate overall system status from service statuses."""
        statuses = [s.status for s in services]

        if all(s == "healthy" for s in statuses):
            return "healthy"
        elif any(s == "unhealthy" for s in statuses):
            return "unhealthy"
        elif any(s == "degraded" for s in statuses):
            return "degraded"
        return "unknown"

    def _calculate_uptime(self) -> float:
        """Calculate approximate uptime from check history."""
        if not self.check_history:
            return 0.0

        first_check = self.check_history[0]["timestamp"]
        try:
            start = datetime.fromisoformat(first_check)
            hours = (datetime.utcnow() - start).total_seconds() / 3600
            return round(hours, 2)
        except Exception:
            return 0.0

    def get_status_summary(self) -> Dict[str, Any]:
        """Get quick status summary without running checks."""
        return {
            "services": {
                name: status.status
                for name, status in self.services.items()
            },
            "last_check": self.check_history[-1]["timestamp"] if self.check_history else None,
            "overall": self.check_history[-1]["overall"] if self.check_history else "unknown"
        }

    def to_dict(self, data: DashboardData) -> Dict[str, Any]:
        """Convert DashboardData to JSON-serializable dict."""
        return {
            "timestamp": data.timestamp,
            "overall_status": data.overall_status,
            "services": [
                {
                    "name": s.name,
                    "status": s.status,
                    "latency_ms": s.latency_ms,
                    "last_check": s.last_check,
                    "details": s.details
                }
                for s in data.services
            ],
            "agents": data.agents,
            "recent_tasks": data.recent_tasks,
            "metrics": data.metrics
        }


# Singleton instance
_dashboard: Optional[HealthDashboard] = None


def get_dashboard() -> HealthDashboard:
    """Get or create dashboard singleton."""
    global _dashboard
    if _dashboard is None:
        _dashboard = HealthDashboard()
    return _dashboard
