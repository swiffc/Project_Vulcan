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

# Phase 15: CAD Drawing Review Bot (ACHE Checker)
from .standards_db import (
    get_beam_properties, get_angle_properties, get_gauge_thickness,
    get_plate_thickness, get_edge_distance, get_standard_hole,
    get_bend_factor, get_density, get_min_fillet_weld, get_fan_tip_clearance,
    calculate_beam_weight, calculate_plate_weight, calculate_angle_weight,
    validate_edge_distance, validate_bend_radius, validate_hole_size, validate_weight,
)
from .drawing_analyzer import (
    DrawingAnalyzer, DrawingPackageAnalysis, PageAnalysis,
    TitleBlock, Dimension, HoleData, BendData, RedFlag,
)
from .weight_calculator import (
    WeightCalculator, WeightResult, WeightValidation, WeightStatus, PartType, PartDimensions,
)
from .hole_pattern_checker import (
    HolePatternChecker, HoleLocation, HoleType, AlignmentResult,
    EdgeDistanceResult, HoleStandardResult, PatternMatch, PatternCheckReport, CheckStatus,
)
from .red_flag_scanner import (
    RedFlagScanner, ScanResult, PartData, Severity, FlagCategory, quick_scan,
)
from .bom_cross_checker import (
    BOMChecker, BOMItem as BOMCheckItem, DrawingPart, ItemMatch, BOMCheckResult, MatchStatus,
)
from .dimension_extractor import (
    DimensionExtractor, ExtractedDimension, ExtractionResult, TitleBlockData,
    Tolerance, DimensionType, Unit,
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
    # Phase 15: CAD Drawing Review Bot
    "get_beam_properties",
    "get_angle_properties",
    "get_gauge_thickness",
    "get_plate_thickness",
    "get_edge_distance",
    "get_standard_hole",
    "get_bend_factor",
    "get_density",
    "get_min_fillet_weld",
    "get_fan_tip_clearance",
    "calculate_beam_weight",
    "calculate_plate_weight",
    "calculate_angle_weight",
    "validate_edge_distance",
    "validate_bend_radius",
    "validate_hole_size",
    "validate_weight",
    "DrawingAnalyzer",
    "DrawingPackageAnalysis",
    "PageAnalysis",
    "TitleBlock",
    "Dimension",
    "HoleData",
    "BendData",
    "RedFlag",
    "WeightCalculator",
    "WeightResult",
    "WeightValidation",
    "WeightStatus",
    "PartType",
    "PartDimensions",
    "HolePatternChecker",
    "HoleLocation",
    "HoleType",
    "AlignmentResult",
    "EdgeDistanceResult",
    "HoleStandardResult",
    "PatternMatch",
    "PatternCheckReport",
    "CheckStatus",
    "RedFlagScanner",
    "ScanResult",
    "PartData",
    "Severity",
    "FlagCategory",
    "quick_scan",
    "BOMChecker",
    "BOMCheckItem",
    "DrawingPart",
    "ItemMatch",
    "BOMCheckResult",
    "MatchStatus",
    "DimensionExtractor",
    "ExtractedDimension",
    "ExtractionResult",
    "TitleBlockData",
    "Tolerance",
    "DimensionType",
    "Unit",
]
