"""
System Manager - Health Monitor
Monitors health of all Vulcan services.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("system-manager.health")


@dataclass
class ServiceHealth:
    """Health status for a single service."""
    name: str
    status: str  # "healthy" | "degraded" | "unhealthy" | "unknown"
    last_check: Optional[str] = None
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


class HealthMonitor:
    """Monitor health of all Vulcan services."""

    def __init__(self):
        self.services: Dict[str, ServiceHealth] = {}
        self.check_history: List[Dict] = []

    def register_service(self, name: str, check_url: Optional[str] = None) -> None:
        """Register a service for health monitoring."""
        self.services[name] = ServiceHealth(
            name=name,
            status="unknown",
            metadata={"check_url": check_url}
        )
        logger.info(f"Registered service for monitoring: {name}")

    def check_all_services(self) -> Dict[str, ServiceHealth]:
        """Run health check on all registered services."""
        logger.info("Running health checks...")
        timestamp = datetime.utcnow().isoformat()

        results = {}
        for name, service in self.services.items():
            try:
                # Perform health check
                health = self._check_service(name)
                health.last_check = timestamp
                self.services[name] = health
                results[name] = health
            except Exception as e:
                self.services[name].status = "unhealthy"
                self.services[name].error_message = str(e)
                self.services[name].last_check = timestamp
                results[name] = self.services[name]

        # Store in history
        self.check_history.append({
            "timestamp": timestamp,
            "results": {name: h.status for name, h in results.items()}
        })

        # Keep only last 100 checks
        if len(self.check_history) > 100:
            self.check_history = self.check_history[-100:]

        healthy_count = sum(1 for h in results.values() if h.status == "healthy")
        logger.info(f"Health check complete: {healthy_count}/{len(results)} healthy")

        return results

    def _check_service(self, name: str) -> ServiceHealth:
        """Check health of a single service."""
        # In production, this would make actual HTTP/TCP checks
        # For now, return healthy status

        return ServiceHealth(
            name=name,
            status="healthy",
            response_time_ms=50.0
        )

    def get_status_summary(self) -> Dict:
        """Get summary of all service health."""
        total = len(self.services)
        healthy = sum(1 for s in self.services.values() if s.status == "healthy")
        degraded = sum(1 for s in self.services.values() if s.status == "degraded")
        unhealthy = sum(1 for s in self.services.values() if s.status == "unhealthy")

        return {
            "total_services": total,
            "healthy": healthy,
            "degraded": degraded,
            "unhealthy": unhealthy,
            "overall_status": "healthy" if healthy == total else "degraded" if unhealthy == 0 else "unhealthy"
        }
