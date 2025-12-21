"""
Notification Store Adapter
Stores notifications for Web UI display.

Phase 11: CAD Performance Manager for 20K+ Part Assemblies
Sends alerts to dashboard for: tier changes, job progress, errors
"""

import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum
import uuid

logger = logging.getLogger("cad_agent.notifications")


class NotificationType(Enum):
    """Types of notifications."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    PROGRESS = "progress"


class NotificationCategory(Enum):
    """Notification categories."""
    PERFORMANCE = "performance"
    JOB = "job"
    CAD = "cad"
    SYSTEM = "system"


@dataclass
class Notification:
    """A notification for the Web UI."""
    id: str
    type: NotificationType
    category: NotificationCategory
    title: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    read: bool = False
    data: Dict = field(default_factory=dict)
    expires_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "category": self.category.value,
            "title": self.title,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "read": self.read,
            "data": self.data,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Notification":
        return cls(
            id=data["id"],
            type=NotificationType(data["type"]),
            category=NotificationCategory(data["category"]),
            title=data["title"],
            message=data["message"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            read=data.get("read", False),
            data=data.get("data", {}),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None
        )


class NotificationStore:
    """
    Stores notifications for Web UI polling.

    Usage:
        store = NotificationStore()

        # Add notification
        store.notify_tier_change("REDUCED", 65.5)

        # Web UI polls
        notifications = store.get_unread()

        # Mark as read
        store.mark_read(notification_id)
    """

    def __init__(self, storage_path: str = "storage/notifications.json",
                 max_notifications: int = 100):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.max_notifications = max_notifications
        self.notifications: List[Notification] = []
        self._load()

    def add(self, type: NotificationType, category: NotificationCategory,
            title: str, message: str, data: Dict = None) -> Notification:
        """Add a notification."""
        notification = Notification(
            id=str(uuid.uuid4())[:8],
            type=type,
            category=category,
            title=title,
            message=message,
            data=data or {}
        )

        self.notifications.insert(0, notification)

        # Trim old notifications
        if len(self.notifications) > self.max_notifications:
            self.notifications = self.notifications[:self.max_notifications]

        self._save()
        logger.info(f"Notification: [{type.value}] {title}")
        return notification

    # Convenience methods for common notifications
    def notify_tier_change(self, new_tier: str, ram_percent: float):
        """Notify about performance tier change."""
        return self.add(
            type=NotificationType.WARNING,
            category=NotificationCategory.PERFORMANCE,
            title=f"Performance Tier: {new_tier}",
            message=f"RAM at {ram_percent:.1f}%. Switched to {new_tier} mode.",
            data={"tier": new_tier, "ram_percent": ram_percent}
        )

    def notify_restart_needed(self, ram_percent: float):
        """Notify that SolidWorks restart is needed."""
        return self.add(
            type=NotificationType.ERROR,
            category=NotificationCategory.PERFORMANCE,
            title="SolidWorks Restart Required",
            message=f"RAM critical at {ram_percent:.1f}%. Restarting SolidWorks...",
            data={"ram_percent": ram_percent}
        )

    def notify_job_progress(self, batch_name: str, completed: int, total: int):
        """Notify about batch job progress."""
        return self.add(
            type=NotificationType.PROGRESS,
            category=NotificationCategory.JOB,
            title=f"Batch: {batch_name}",
            message=f"Progress: {completed}/{total} ({completed/total*100:.0f}%)",
            data={"batch": batch_name, "completed": completed, "total": total}
        )

    def notify_job_complete(self, batch_name: str, completed: int, failed: int):
        """Notify that batch job completed."""
        type = NotificationType.SUCCESS if failed == 0 else NotificationType.WARNING
        return self.add(
            type=type,
            category=NotificationCategory.JOB,
            title=f"Batch Complete: {batch_name}",
            message=f"Completed: {completed}, Failed: {failed}",
            data={"batch": batch_name, "completed": completed, "failed": failed}
        )

    def notify_job_error(self, file_path: str, error: str):
        """Notify about job error."""
        return self.add(
            type=NotificationType.ERROR,
            category=NotificationCategory.JOB,
            title="Job Failed",
            message=f"{Path(file_path).name}: {error}",
            data={"file": file_path, "error": error}
        )

    def notify_cad_connected(self, app_name: str):
        """Notify CAD connection."""
        return self.add(
            type=NotificationType.SUCCESS,
            category=NotificationCategory.CAD,
            title=f"{app_name} Connected",
            message=f"Successfully connected to {app_name}",
            data={"app": app_name}
        )

    def notify_cad_error(self, app_name: str, error: str):
        """Notify CAD error."""
        return self.add(
            type=NotificationType.ERROR,
            category=NotificationCategory.CAD,
            title=f"{app_name} Error",
            message=error,
            data={"app": app_name, "error": error}
        )

    def get_all(self, limit: int = 50) -> List[Dict]:
        """Get all notifications."""
        return [n.to_dict() for n in self.notifications[:limit]]

    def get_unread(self) -> List[Dict]:
        """Get unread notifications."""
        return [n.to_dict() for n in self.notifications if not n.read]

    def get_by_category(self, category: NotificationCategory) -> List[Dict]:
        """Get notifications by category."""
        return [n.to_dict() for n in self.notifications if n.category == category]

    def mark_read(self, notification_id: str):
        """Mark notification as read."""
        for n in self.notifications:
            if n.id == notification_id:
                n.read = True
                self._save()
                return True
        return False

    def mark_all_read(self):
        """Mark all notifications as read."""
        for n in self.notifications:
            n.read = True
        self._save()

    def clear_old(self, hours: int = 24):
        """Clear notifications older than N hours."""
        cutoff = datetime.now()
        from datetime import timedelta
        cutoff = cutoff - timedelta(hours=hours)

        original = len(self.notifications)
        self.notifications = [n for n in self.notifications
                             if n.timestamp > cutoff]
        removed = original - len(self.notifications)

        if removed > 0:
            self._save()
            logger.info(f"Cleared {removed} old notifications")

    def _save(self):
        """Save to disk."""
        data = [n.to_dict() for n in self.notifications]
        self.storage_path.write_text(json.dumps(data, indent=2))

    def _load(self):
        """Load from disk."""
        if not self.storage_path.exists():
            return

        try:
            data = json.loads(self.storage_path.read_text())
            self.notifications = [Notification.from_dict(d) for d in data]
            logger.info(f"Loaded {len(self.notifications)} notifications")
        except Exception as e:
            logger.error(f"Failed to load notifications: {e}")


# Singleton
_store: Optional[NotificationStore] = None

def get_notification_store() -> NotificationStore:
    global _store
    if _store is None:
        _store = NotificationStore()
    return _store
