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
]
