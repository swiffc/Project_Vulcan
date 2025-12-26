"""
CAD Validation Orchestration System

Coordinates all validation checks (GDT, welding, material, ACHE)
and generates comprehensive validation reports.

Phase 25 - Added PDF Drawing Validation support.
"""

from .orchestrator import ValidationOrchestrator
from .drawing_analyzer import DrawingAnalyzer
from .validation_models import (
    ValidationRequest,
    ValidationReport,
    ValidationStatus,
    ValidationIssue,
    ValidationSeverity,
    GDTValidationResult,
    WeldValidationResult,
    MaterialValidationResult,
    ACHEValidationResult,
)

# Phase 25 - PDF Validation
from .api_661_validator import API661Validator, API661ValidationResult
from .asme_validator import ASMEValidator, ASMEValidationResult
from .aws_d1_1_validator import AWSD11Validator, AWSValidationResult
from .pdf_validation_engine import PDFValidationEngine, PDFValidationResult, validate_pdf

# Phase 25.5-25.8 - Additional Validators
from .osha_validator import OSHAValidator, OSHAValidationResult
from .bom_validator import BOMValidator, BOMValidationResult
from .dimension_validator import DimensionValidator, DimensionValidationResult
from .drawing_completeness_validator import DrawingCompletenessValidator, CompletenessValidationResult

# Phase 25 Drawing Checker - New Validators
from .aisc_hole_validator import AISCHoleValidator, AISCHoleValidationResult, HoleData
from .structural_capacity_validator import StructuralCapacityValidator, StructuralValidationResult, BoltData, WeldData
from .shaft_validator import ShaftValidator, ShaftValidationResult, ShaftData, KeywayData
from .handling_validator import HandlingValidator, HandlingValidationResult, HandlingData

# Phase 25 - ACHE Standards Database Validators
from .api661_bundle_validator import API661BundleValidator, API661BundleValidationResult, BundleData, FanData, DriveData
from .api661_full_scope_validator import (
    API661FullScopeValidator, API661FullResult, API661FullData,
    HeaderType, JointType, FinType, DriveType
)
from .nema_motor_validator import NEMAMotorValidator, NEMAMotorValidationResult, MotorData
from .sspc_coating_validator import SSPCCoatingValidator, SSPCValidationResult, CoatingSpec
from .asme_viii_validator import ASMEVIIIValidator, ASMEVIIIValidationResult, VesselData
from .tema_validator import TEMAValidator, TEMAValidationResult, HeatExchangerData, TEMAClass

# Phase 25 - Final Standards Validators (100% Coverage)
from .geometry_profile_validator import (
    GeometryProfileValidator, GeometryValidationResult,
    CornerData, CopeData, NotchData, WebOpeningData
)
from .tolerance_validator import (
    ToleranceValidator, ToleranceValidationResult,
    FlatnessData, SquarenessData, ParallelismData
)
from .sheet_metal_validator import (
    SheetMetalValidator, SheetMetalValidationResult, BendData
)
from .member_capacity_validator import (
    MemberCapacityValidator, MemberCapacityResult, MemberData
)

# Phase 25.3-25.12 - New Validators
from .fabrication_feasibility_validator import (
    FabricationFeasibilityValidator, FabricationValidationResult,
    PartGeometry, FabricationProcess
)
from .inspection_qc_validator import (
    InspectionQCValidator, InspectionValidationResult,
    WeldInspectionData, InspectionPlanData, NDEMethod, WeldCategory
)
from .cross_part_validator import (
    CrossPartValidator, CrossPartValidationResult,
    PartInterface, HolePattern, InterfaceType, FitClass
)

# Phase 25.5-25.13 - Additional Validators
from .shaft_validator import (
    MachiningToleranceValidator, MachiningToleranceResult,
    MachiningToleranceData, PROCESS_TOLERANCES, FIT_CLASSES
)
from .materials_finishing_validator import (
    MaterialsFinishingValidator, MaterialsValidationResult,
    MaterialSpec, CoatingSpec, MaterialCategory, SurfacePrep
)
from .fastener_validator import (
    FastenerValidator, FastenerValidationResult,
    BoltData, ConnectionData, BoltGrade, ConnectionType, HoleType
)
from .rigging_validator import (
    RiggingValidator, RiggingValidationResult,
    LiftingLugData, RiggingData, LoadClass, LiftingDeviceType
)
from .documentation_validator import (
    DocumentationValidator, DocumentationValidationResult,
    TitleBlockData, DrawingNotes, DrawingType, DocumentationLevel
)
from .report_generator import (
    ReportGenerator, ValidationReport, ValidatorSummary,
    ReportMetadata, ReportFormat, ReportLevel
)

__all__ = [
    # Core validators
    "ValidationOrchestrator",
    "DrawingAnalyzer",
    # Validation models
    "ValidationRequest",
    "ValidationReport",
    "ValidationStatus",
    "ValidationIssue",
    "ValidationSeverity",
    "GDTValidationResult",
    "WeldValidationResult",
    "MaterialValidationResult",
    "ACHEValidationResult",
    # Phase 25 - PDF Validators
    "API661Validator",
    "API661ValidationResult",
    "ASMEValidator",
    "ASMEValidationResult",
    "AWSD11Validator",
    "AWSValidationResult",
    "PDFValidationEngine",
    "PDFValidationResult",
    "validate_pdf",
    # Phase 25.5-25.8 - Additional Validators
    "OSHAValidator",
    "OSHAValidationResult",
    "BOMValidator",
    "BOMValidationResult",
    "DimensionValidator",
    "DimensionValidationResult",
    "DrawingCompletenessValidator",
    "CompletenessValidationResult",
    # Phase 25 Drawing Checker - New
    "AISCHoleValidator",
    "AISCHoleValidationResult",
    "HoleData",
    "StructuralCapacityValidator",
    "StructuralValidationResult",
    "BoltData",
    "WeldData",
    "ShaftValidator",
    "ShaftValidationResult",
    "ShaftData",
    "KeywayData",
    "HandlingValidator",
    "HandlingValidationResult",
    "HandlingData",
    # Phase 25 - ACHE Standards Database
    "API661BundleValidator",
    "API661BundleValidationResult",
    "BundleData",
    "FanData",
    "DriveData",
    # API 661 Full Scope (82 checks)
    "API661FullScopeValidator",
    "API661FullResult",
    "API661FullData",
    "HeaderType",
    "JointType",
    "FinType",
    "DriveType",
    "NEMAMotorValidator",
    "NEMAMotorValidationResult",
    "MotorData",
    "SSPCCoatingValidator",
    "SSPCValidationResult",
    "CoatingSpec",
    "ASMEVIIIValidator",
    "ASMEVIIIValidationResult",
    "VesselData",
    "TEMAValidator",
    "TEMAValidationResult",
    "HeatExchangerData",
    "TEMAClass",
    # Phase 25 - Final Standards (100% Coverage)
    "GeometryProfileValidator",
    "GeometryValidationResult",
    "CornerData",
    "CopeData",
    "NotchData",
    "WebOpeningData",
    "ToleranceValidator",
    "ToleranceValidationResult",
    "FlatnessData",
    "SquarenessData",
    "ParallelismData",
    "SheetMetalValidator",
    "SheetMetalValidationResult",
    "BendData",
    "MemberCapacityValidator",
    "MemberCapacityResult",
    "MemberData",
    # Phase 25.3-25.12 - New Validators
    "FabricationFeasibilityValidator",
    "FabricationValidationResult",
    "PartGeometry",
    "FabricationProcess",
    "InspectionQCValidator",
    "InspectionValidationResult",
    "WeldInspectionData",
    "InspectionPlanData",
    "NDEMethod",
    "WeldCategory",
    "CrossPartValidator",
    "CrossPartValidationResult",
    "PartInterface",
    "HolePattern",
    "InterfaceType",
    "FitClass",
]
