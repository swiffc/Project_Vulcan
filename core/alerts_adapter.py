"""
Alerts Adapter - Monitoring Notifications

Thin wrapper for sending alerts to Slack, PagerDuty, and email.
Integrates with health dashboard for automatic alerting.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger("core.alerts")


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertChannel(Enum):
    """Alert delivery channels."""
    SLACK = "slack"
    PAGERDUTY = "pagerduty"
    EMAIL = "email"
    WEBHOOK = "webhook"


@dataclass
class Alert:
    """Alert data structure."""
    title: str
    message: str
    severity: AlertSeverity
    source: str
    timestamp: str = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class AlertConfig:
    """Alert configuration."""
    slack_webhook: str = None
    pagerduty_key: str = None
    email_smtp: str = None
    email_to: List[str] = None
    webhook_url: str = None

    def __post_init__(self):
        self.slack_webhook = self.slack_webhook or os.getenv("SLACK_WEBHOOK_URL")
        self.pagerduty_key = self.pagerduty_key or os.getenv("PAGERDUTY_ROUTING_KEY")
        self.email_smtp = self.email_smtp or os.getenv("SMTP_SERVER")
        self.webhook_url = self.webhook_url or os.getenv("ALERT_WEBHOOK_URL")


class AlertsAdapter:
    """
    Alerts adapter for multi-channel notifications.

    Supports:
    - Slack webhooks
    - PagerDuty events
    - Email notifications
    - Generic webhooks
    """

    def __init__(self, config: AlertConfig = None):
        self.config = config or AlertConfig()
        self._history: List[Alert] = []
        self._max_history = 100

    async def send(
        self,
        alert: Alert,
        channels: List[AlertChannel] = None
    ) -> Dict[str, bool]:
        """
        Send alert to specified channels.

        Args:
            alert: Alert to send
            channels: Target channels (default: all configured)

        Returns:
            Dict of channel -> success status
        """
        if channels is None:
            channels = self._get_configured_channels()

        results = {}
        for channel in channels:
            try:
                if channel == AlertChannel.SLACK:
                    results["slack"] = await self._send_slack(alert)
                elif channel == AlertChannel.PAGERDUTY:
                    results["pagerduty"] = await self._send_pagerduty(alert)
                elif channel == AlertChannel.EMAIL:
                    results["email"] = await self._send_email(alert)
                elif channel == AlertChannel.WEBHOOK:
                    results["webhook"] = await self._send_webhook(alert)
            except Exception as e:
                logger.error(f"Failed to send to {channel.value}: {e}")
                results[channel.value] = False

        self._store_history(alert)
        return results

    def _get_configured_channels(self) -> List[AlertChannel]:
        """Get list of configured channels."""
        channels = []
        if self.config.slack_webhook:
            channels.append(AlertChannel.SLACK)
        if self.config.pagerduty_key:
            channels.append(AlertChannel.PAGERDUTY)
        if self.config.email_smtp:
            channels.append(AlertChannel.EMAIL)
        if self.config.webhook_url:
            channels.append(AlertChannel.WEBHOOK)
        return channels

    async def _send_slack(self, alert: Alert) -> bool:
        """Send alert to Slack."""
        import httpx

        color_map = {
            AlertSeverity.INFO: "#36a64f",
            AlertSeverity.WARNING: "#ffcc00",
            AlertSeverity.ERROR: "#ff6600",
            AlertSeverity.CRITICAL: "#ff0000",
        }

        payload = {
            "attachments": [{
                "color": color_map.get(alert.severity, "#808080"),
                "title": f"[{alert.severity.value.upper()}] {alert.title}",
                "text": alert.message,
                "fields": [
                    {"title": "Source", "value": alert.source, "short": True},
                    {"title": "Time", "value": alert.timestamp, "short": True},
                ],
                "footer": "Vulcan Alerts"
            }]
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(self.config.slack_webhook, json=payload)
            return resp.status_code == 200

    async def _send_pagerduty(self, alert: Alert) -> bool:
        """Send alert to PagerDuty."""
        import httpx

        severity_map = {
            AlertSeverity.INFO: "info",
            AlertSeverity.WARNING: "warning",
            AlertSeverity.ERROR: "error",
            AlertSeverity.CRITICAL: "critical",
        }

        payload = {
            "routing_key": self.config.pagerduty_key,
            "event_action": "trigger",
            "payload": {
                "summary": f"{alert.title}: {alert.message}",
                "severity": severity_map.get(alert.severity, "info"),
                "source": alert.source,
                "timestamp": alert.timestamp,
                "custom_details": alert.metadata
            }
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://events.pagerduty.com/v2/enqueue",
                json=payload
            )
            return resp.status_code == 202

    async def _send_email(self, alert: Alert) -> bool:
        """Send alert via email."""
        import smtplib
        from email.mime.text import MIMEText

        if not self.config.email_to:
            return False

        msg = MIMEText(f"{alert.message}\n\nSource: {alert.source}\nTime: {alert.timestamp}")
        msg["Subject"] = f"[Vulcan {alert.severity.value.upper()}] {alert.title}"
        msg["From"] = "vulcan@localhost"
        msg["To"] = ", ".join(self.config.email_to)

        try:
            with smtplib.SMTP(self.config.email_smtp) as server:
                server.send_message(msg)
            return True
        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return False

    async def _send_webhook(self, alert: Alert) -> bool:
        """Send alert to generic webhook."""
        import httpx

        payload = {
            "title": alert.title,
            "message": alert.message,
            "severity": alert.severity.value,
            "source": alert.source,
            "timestamp": alert.timestamp,
            "metadata": alert.metadata
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(self.config.webhook_url, json=payload)
            return resp.status_code < 400

    def _store_history(self, alert: Alert):
        """Store alert in history."""
        self._history.append(alert)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

    def get_history(self, limit: int = 20) -> List[Dict]:
        """Get recent alert history."""
        return [
            {
                "title": a.title,
                "message": a.message,
                "severity": a.severity.value,
                "source": a.source,
                "timestamp": a.timestamp
            }
            for a in self._history[-limit:]
        ]

    async def check_health_and_alert(self):
        """Check health dashboard and send alerts for issues."""
        from .health_dashboard import get_dashboard

        dashboard = get_dashboard()
        status = dashboard.get_status_summary()

        for service, health in status.get("services", {}).items():
            if health == "unhealthy":
                await self.send(Alert(
                    title=f"Service Down: {service}",
                    message=f"The {service} service is reporting unhealthy status",
                    severity=AlertSeverity.CRITICAL,
                    source="health_monitor"
                ))
            elif health == "degraded":
                await self.send(Alert(
                    title=f"Service Degraded: {service}",
                    message=f"The {service} service is experiencing issues",
                    severity=AlertSeverity.WARNING,
                    source="health_monitor"
                ))


# Singleton
_alerts: Optional[AlertsAdapter] = None


def get_alerts_adapter(config: AlertConfig = None) -> AlertsAdapter:
    """Get or create alerts adapter singleton."""
    global _alerts
    if _alerts is None:
        _alerts = AlertsAdapter(config)
    return _alerts
