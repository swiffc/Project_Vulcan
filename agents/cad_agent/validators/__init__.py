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
from .nema_motor_validator import NEMAMotorValidator, NEMAMotorValidationResult, MotorData
from .sspc_coating_validator import SSPCCoatingValidator, SSPCValidationResult, CoatingSpec

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
    "NEMAMotorValidator",
    "NEMAMotorValidationResult",
    "MotorData",
    "SSPCCoatingValidator",
    "SSPCValidationResult",
    "CoatingSpec",
]
