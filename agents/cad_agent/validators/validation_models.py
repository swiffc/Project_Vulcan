"""
Validation Data Models

Pydantic models for validation requests, reports, and results.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class ValidationStatus(str, Enum):
    """Validation execution status."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETE = "complete"
    ERROR = "error"


class ValidationSeverity(str, Enum):
    """Issue severity levels."""

    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationIssue(BaseModel):
    """Individual validation issue."""

    severity: ValidationSeverity
    check_type: str  # "gdt", "welding", "material", etc.
    message: str
    location: Optional[str] = None  # Page/section reference
    suggestion: Optional[str] = None
    standard_reference: Optional[str] = None  # e.g., "ASME Y14.5-2018"


class GDTValidationResult(BaseModel):
    """GD&T validation results."""

    total_features: int = 0
    valid_features: int = 0
    invalid_features: int = 0
    issues: List[ValidationIssue] = Field(default_factory=list)
    datums_found: List[str] = Field(default_factory=list)
    tolerances_parsed: int = 0


class WeldValidationResult(BaseModel):
    """Welding validation results."""

    total_welds: int = 0
    compliant_welds: int = 0
    non_compliant_welds: int = 0
    issues: List[ValidationIssue] = Field(default_factory=list)
    aws_d11_compliant: bool = True
    weld_symbols_found: List[str] = Field(default_factory=list)


class MaterialValidationResult(BaseModel):
    """Material validation results."""

    materials_validated: int = 0
    mtrs_found: int = 0
    compliant_materials: int = 0
    issues: List[ValidationIssue] = Field(default_factory=list)
    astm_specs_checked: List[str] = Field(default_factory=list)
    carbon_equivalent_ok: bool = True


class ACHEValidationResult(BaseModel):
    """ACHE 130-point validation results."""

    total_checks: int = 130
    passed: int = 0
    warnings: int = 0
    errors: int = 0
    critical_failures: int = 0
    issues: List[ValidationIssue] = Field(default_factory=list)
    category_scores: Dict[str, float] = Field(default_factory=dict)


class DrawingValidationResult(BaseModel):
    """Drawing validation results."""

    total_checks: int = 0
    passed: int = 0
    warnings: int = 0
    errors: int = 0
    issues: List[ValidationIssue] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    dimensions_count: int = 0
    notes_count: int = 0
    bom_items_count: int = 0
    layers_found: List[str] = Field(default_factory=list)


class ValidationRequest(BaseModel):
    """User validation request."""

    type: Literal["drawing", "assembly", "ache", "custom"]
    file_path: Optional[str] = None
    file_id: Optional[str] = None  # Flatter Files ID
    checks: List[str] = Field(default_factory=lambda: ["all"])
    severity: Literal["critical", "all"] = "all"
    user_id: str
    project_id: Optional[str] = None
    custom_checklist: Optional[List[str]] = None


class ValidationReport(BaseModel):
    """Complete validation results."""

    id: str
    request_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    duration_ms: int
    status: ValidationStatus = ValidationStatus.COMPLETE

    # Results by check type
    gdt_results: Optional[GDTValidationResult] = None
    welding_results: Optional[WeldValidationResult] = None
    material_results: Optional[MaterialValidationResult] = None
    ache_results: Optional[ACHEValidationResult] = None
    drawing_results: Optional[DrawingValidationResult] = None  # Added field

    # Phase 25 - Drawing Checker results (holes, structural, shaft, handling, etc.)
    phase25_results: Optional[Dict[str, Any]] = None

    # Summary
    total_checks: int = 0
    passed: int = 0
    warnings: int = 0
    errors: int = 0
    critical_failures: int = 0
    pass_rate: float = 0.0

    # All issues combined
    all_issues: List[ValidationIssue] = Field(default_factory=list)

    # Files
    input_file: str
    annotated_pdf: Optional[str] = None
    report_pdf: Optional[str] = None

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def calculate_summary(self) -> None:
        """Calculate summary statistics from all results."""
        self.total_checks = 0
        self.passed = 0
        self.warnings = 0
        self.errors = 0
        self.critical_failures = 0
        self.all_issues = []

        # GDT results
        if self.gdt_results:
            self.total_checks += self.gdt_results.total_features
            self.passed += self.gdt_results.valid_features
            self.all_issues.extend(self.gdt_results.issues)

        # Welding results
        if self.welding_results:
            self.total_checks += self.welding_results.total_welds
            self.passed += self.welding_results.compliant_welds
            self.all_issues.extend(self.welding_results.issues)

        # Material results
        if self.material_results:
            self.total_checks += self.material_results.materials_validated
            self.passed += self.material_results.compliant_materials
            self.all_issues.extend(self.material_results.issues)

        # ACHE results
        if self.ache_results:
            self.total_checks += self.ache_results.total_checks
            self.passed += self.ache_results.passed
            self.warnings += self.ache_results.warnings
            self.errors += self.ache_results.errors
            self.critical_failures += self.ache_results.critical_failures
            self.all_issues.extend(self.ache_results.issues)

        # Count severity levels from all issues
        for issue in self.all_issues:
            if issue.severity == ValidationSeverity.CRITICAL:
                self.critical_failures += 1
            elif issue.severity == ValidationSeverity.ERROR:
                self.errors += 1
            elif issue.severity == ValidationSeverity.WARNING:
                self.warnings += 1

        # Calculate pass rate
        if self.total_checks > 0:
            self.pass_rate = (self.passed / self.total_checks) * 100
        else:
            self.pass_rate = 0.0


class ValidationProgress(BaseModel):
    """Real-time validation progress."""

    request_id: str
    status: ValidationStatus
    current_step: str
    progress_percent: int = 0
    message: str = ""
    started_at: datetime = Field(default_factory=datetime.now)
    estimated_completion: Optional[datetime] = None
