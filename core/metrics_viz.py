"""
Metrics Visualization - Dashboard Data Provider

Aggregates system metrics for dashboard visualization.
Provides chart-ready data structures.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger("core.metrics_viz")


@dataclass
class TimeSeriesPoint:
    """Single point in time series."""
    timestamp: str
    value: float
    label: Optional[str] = None


@dataclass
class ChartData:
    """Chart-ready data structure."""
    title: str
    chart_type: str  # "line", "bar", "pie", "gauge"
    data: List[TimeSeriesPoint]
    config: Dict[str, Any] = field(default_factory=dict)


class MetricsViz:
    """
    Metrics visualization provider.

    Aggregates data from:
    - Health dashboard
    - Task history
    - Agent performance
    """

    def __init__(self):
        self.history: Dict[str, List[TimeSeriesPoint]] = defaultdict(list)
        self._max_points = 100

    def record(self, metric: str, value: float, label: str = None):
        """Record a metric value."""
        point = TimeSeriesPoint(
            timestamp=datetime.utcnow().isoformat(),
            value=value,
            label=label
        )
        self.history[metric].append(point)

        # Trim old data
        if len(self.history[metric]) > self._max_points:
            self.history[metric] = self.history[metric][-self._max_points:]

    def get_uptime_chart(self, hours: int = 24) -> ChartData:
        """Get system uptime chart data."""
        points = self._get_recent_points("uptime", hours)
        return ChartData(
            title="System Uptime",
            chart_type="line",
            data=points,
            config={"yAxis": {"min": 0, "max": 100}, "unit": "%"}
        )

    def get_response_time_chart(self, hours: int = 24) -> ChartData:
        """Get response time chart data."""
        points = self._get_recent_points("response_time", hours)
        return ChartData(
            title="Response Time",
            chart_type="line",
            data=points,
            config={"yAxis": {"min": 0}, "unit": "ms"}
        )

    def get_agent_usage_chart(self) -> ChartData:
        """Get agent usage distribution (pie chart)."""
        from .orchestrator_adapter import get_orchestrator

        try:
            orch = get_orchestrator()
            history = orch.get_task_history(limit=100)

            counts = defaultdict(int)
            for task in history:
                counts[task.get("agent", "unknown")] += 1

            points = [
                TimeSeriesPoint(
                    timestamp=datetime.utcnow().isoformat(),
                    value=count,
                    label=agent
                )
                for agent, count in counts.items()
            ]

            return ChartData(
                title="Agent Usage",
                chart_type="pie",
                data=points,
                config={"showLegend": True}
            )
        except Exception:
            return ChartData(
                title="Agent Usage",
                chart_type="pie",
                data=[],
                config={"error": "No data available"}
            )

    def get_success_rate_gauge(self) -> ChartData:
        """Get task success rate gauge."""
        from .orchestrator_adapter import get_orchestrator

        try:
            orch = get_orchestrator()
            history = orch.get_task_history(limit=100)

            if not history:
                rate = 0
            else:
                success = sum(1 for t in history if t.get("success"))
                rate = (success / len(history)) * 100

            return ChartData(
                title="Success Rate",
                chart_type="gauge",
                data=[TimeSeriesPoint(
                    timestamp=datetime.utcnow().isoformat(),
                    value=round(rate, 1)
                )],
                config={"min": 0, "max": 100, "unit": "%"}
            )
        except Exception:
            return ChartData(
                title="Success Rate",
                chart_type="gauge",
                data=[TimeSeriesPoint(
                    timestamp=datetime.utcnow().isoformat(),
                    value=0
                )],
                config={"min": 0, "max": 100, "unit": "%"}
            )

    def get_service_health_chart(self) -> ChartData:
        """Get service health status bars."""
        from .health_dashboard import get_dashboard

        try:
            dashboard = get_dashboard()
            status = dashboard.get_status_summary()

            points = []
            status_values = {"healthy": 100, "degraded": 50, "unhealthy": 0, "unknown": 25}

            for service, health in status.get("services", {}).items():
                points.append(TimeSeriesPoint(
                    timestamp=datetime.utcnow().isoformat(),
                    value=status_values.get(health, 0),
                    label=service
                ))

            return ChartData(
                title="Service Health",
                chart_type="bar",
                data=points,
                config={"horizontal": True, "colors": {
                    100: "#22c55e", 50: "#eab308", 0: "#ef4444", 25: "#6b7280"
                }}
            )
        except Exception:
            return ChartData(
                title="Service Health",
                chart_type="bar",
                data=[],
                config={"error": "No data available"}
            )

    def get_dashboard_data(self) -> Dict[str, ChartData]:
        """Get all dashboard charts."""
        return {
            "uptime": self.get_uptime_chart(),
            "response_time": self.get_response_time_chart(),
            "agent_usage": self.get_agent_usage_chart(),
            "success_rate": self.get_success_rate_gauge(),
            "service_health": self.get_service_health_chart(),
        }

    def to_dict(self, charts: Dict[str, ChartData]) -> Dict[str, Any]:
        """Convert charts to JSON-serializable dict."""
        return {
            name: {
                "title": chart.title,
                "type": chart.chart_type,
                "data": [
                    {"timestamp": p.timestamp, "value": p.value, "label": p.label}
                    for p in chart.data
                ],
                "config": chart.config
            }
            for name, chart in charts.items()
        }

    def _get_recent_points(self, metric: str, hours: int) -> List[TimeSeriesPoint]:
        """Get points from the last N hours."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return [
            p for p in self.history.get(metric, [])
            if datetime.fromisoformat(p.timestamp) > cutoff
        ]


# Singleton instance
_metrics: Optional[MetricsViz] = None


def get_metrics_viz() -> MetricsViz:
    """Get or create metrics viz singleton."""
    global _metrics
    if _metrics is None:
        _metrics = MetricsViz()
    return _metrics
