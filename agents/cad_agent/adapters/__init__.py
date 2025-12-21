"""
CAD Agent Adapters
Thin wrappers around external packages for CAD pipeline.
"""

from .pdf_bridge import PDFBridge
from .ecn_adapter import ECNAdapter
from .gdrive_bridge import GDriveBridge
from .digital_twin import DigitalTwinAdapter, get_digital_twin_adapter

# Phase 11: CAD Performance Manager
from .performance_manager import (
    PerformanceManager, get_performance_manager, PerformanceTier
)
from .solidworks_settings import (
    SolidWorksSettingsAdapter, get_solidworks_settings, GraphicsSettings
)
from .job_queue import (
    JobQueueAdapter, get_job_queue, Job, JobType, JobStatus
)
from .notification_store import (
    NotificationStore, get_notification_store, Notification, NotificationType
)

# Phase 12: Flatter Files Integration
from .flatter_files_adapter import (
    FlatterFilesAdapter, get_flatter_files_adapter, FlatterItem, BOMItem
)

__all__ = [
    # Existing
    "PDFBridge",
    "ECNAdapter",
    "GDriveBridge",
    "DigitalTwinAdapter",
    "get_digital_twin_adapter",
    # Phase 11
    "PerformanceManager",
    "get_performance_manager",
    "PerformanceTier",
    "SolidWorksSettingsAdapter",
    "get_solidworks_settings",
    "GraphicsSettings",
    "JobQueueAdapter",
    "get_job_queue",
    "Job",
    "JobType",
    "JobStatus",
    "NotificationStore",
    "get_notification_store",
    "Notification",
    "NotificationType",
    # Phase 12
    "FlatterFilesAdapter",
    "get_flatter_files_adapter",
    "FlatterItem",
    "BOMItem",
]
