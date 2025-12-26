"""
PDF Validation Engine
=====================
Unified validation engine for engineering drawing PDFs.
Orchestrates extraction and validation against multiple standards.

Phase 25 Implementation
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import uuid

from .validation_models import ValidationIssue, ValidationSeverity
from .api_661_validator import API661Validator, API661ValidationResult
from .asme_validator import ASMEValidator, ASMEValidationResult
from .aws_d1_1_validator import AWSD11Validator, AWSValidationResult
from .osha_validator import OSHAValidator, OSHAValidationResult
from .bom_validator import BOMValidator, BOMValidationResult
from .dimension_validator import DimensionValidator, DimensionValidationResult
from .drawing_completeness_validator import DrawingCompletenessValidator, CompletenessValidationResult

# Phase 26 - HPC Standards Validators
from .hpc_mechanical_validator import HPCMechanicalValidator, HPCMechanicalValidationResult
from .hpc_walkway_validator import HPCWalkwayValidator, HPCWalkwayValidationResult
from .hpc_header_validator import HPCHeaderValidator, HPCHeaderValidationResult

# Import PDF extractor
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "desktop_server"))
try:
    from extractors.pdf_drawing_extractor import PDFDrawingExtractor, DrawingExtractionResult, DrawingType
except ImportError:
    PDFDrawingExtractor = None
    DrawingExtractionResult = None
    DrawingType = None

logger = logging.getLogger("vulcan.validator.pdf_engine")


@dataclass
class PDFValidationResult:
    """Complete PDF validation result."""
    id: str = ""
    file_path: str = ""
    file_name: str = ""
    timestamp: str = ""
    duration_ms: int = 0
    drawing_type: str = ""

    # Extraction summary
    extraction_success: bool = False
    extraction_errors: List[str] = field(default_factory=list)
    page_count: int = 0
    part_number: str = ""
    revision: str = ""

    # Validation results by standard
    api_661_results: Optional[Dict[str, Any]] = None
    asme_results: Optional[Dict[str, Any]] = None
    aws_d1_1_results: Optional[Dict[str, Any]] = None
    osha_results: Optional[Dict[str, Any]] = None
    bom_results: Optional[Dict[str, Any]] = None
    dimension_results: Optional[Dict[str, Any]] = None
    completeness_results: Optional[Dict[str, Any]] = None

    # Phase 26 - HPC Standards results
    hpc_mechanical_results: Optional[Dict[str, Any]] = None
    hpc_walkway_results: Optional[Dict[str, Any]] = None
    hpc_header_results: Optional[Dict[str, Any]] = None

    # Summary statistics
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    pass_rate: float = 0.0

    # All issues combined
    all_issues: List[Dict[str, Any]] = field(default_factory=list)

    # Severity breakdown
    severity_counts: Dict[str, int] = field(default_factory=dict)


class PDFValidationEngine:
    """
    Unified PDF validation engine.

    Orchestrates:
    1. PDF extraction (text, BOM, dimensions, welds, etc.)
    2. API 661 validation (ACHE standards)
    3. ASME validation (pressure vessels)
    4. AWS D1.1 validation (welding)
    5. OSHA validation (structural safety)
    6. BOM validation (bill of materials)
    7. Dimension validation (measurements)
    8. Completeness validation (drawing requirements)
    9. Result aggregation and reporting
    """

    def __init__(self):
        """Initialize the validation engine."""
        self.extractor = PDFDrawingExtractor() if PDFDrawingExtractor else None
        self.api_661 = API661Validator()
        self.asme = ASMEValidator()
        self.aws_d1_1 = AWSD11Validator()
        self.osha = OSHAValidator()
        self.bom = BOMValidator()
        self.dimension = DimensionValidator()
        self.completeness = DrawingCompletenessValidator()

        # Phase 26 - HPC Standards Validators
        self.hpc_mechanical = HPCMechanicalValidator()
        self.hpc_walkway = HPCWalkwayValidator()
        self.hpc_header = HPCHeaderValidator()

        if not self.extractor:
            logger.warning("PDFDrawingExtractor not available - extraction will fail")

    def validate(
        self,
        pdf_path: str,
        standards: Optional[List[str]] = None
    ) -> PDFValidationResult:
        """
        Validate a PDF drawing against engineering standards.

        Args:
            pdf_path: Path to the PDF file
            standards: List of standards to check (default: all)
                       Options: ["api_661", "asme", "aws_d1_1"]

        Returns:
            PDFValidationResult with all validation results
        """
        start_time = time.time()

        result = PDFValidationResult(
            id=str(uuid.uuid4()),
            file_path=pdf_path,
            file_name=Path(pdf_path).name,
            timestamp=datetime.now().isoformat(),
        )

        # Default to all standards
        if standards is None:
            standards = ["api_661", "asme", "aws_d1_1", "osha", "bom", "dimension", "completeness",
                        "hpc_mechanical", "hpc_walkway", "hpc_header"]

        # Step 1: Extract data from PDF
        if not self.extractor:
            result.extraction_errors.append("PDF extractor not available")
            result.duration_ms = int((time.time() - start_time) * 1000)
            return result

        logger.info(f"Extracting data from: {pdf_path}")
        extraction = self.extractor.extract(pdf_path)

        if extraction.extraction_errors:
            result.extraction_errors = extraction.extraction_errors

        result.extraction_success = len(extraction.extraction_errors) == 0
        result.page_count = extraction.page_count
        result.drawing_type = extraction.drawing_type.value if extraction.drawing_type else "UNKNOWN"
        result.part_number = extraction.title_block.part_number
        result.revision = extraction.title_block.revision

        # Step 2: Run validations
        if "api_661" in standards:
            logger.info("Running API 661 validation...")
            api_result = self.api_661.validate(extraction)
            result.api_661_results = self.api_661.to_dict(api_result)
            self._aggregate_results(result, api_result)

        if "asme" in standards:
            logger.info("Running ASME validation...")
            asme_result = self.asme.validate(extraction)
            result.asme_results = self.asme.to_dict(asme_result)
            self._aggregate_results(result, asme_result)

        if "aws_d1_1" in standards:
            logger.info("Running AWS D1.1 validation...")
            aws_result = self.aws_d1_1.validate(extraction)
            result.aws_d1_1_results = self.aws_d1_1.to_dict(aws_result)
            self._aggregate_results(result, aws_result)

        if "osha" in standards:
            logger.info("Running OSHA structural validation...")
            osha_result = self.osha.validate(extraction)
            result.osha_results = self.osha.to_dict(osha_result)
            self._aggregate_results(result, osha_result)

        if "bom" in standards:
            logger.info("Running BOM validation...")
            bom_result = self.bom.validate(extraction)
            result.bom_results = self.bom.to_dict(bom_result)
            self._aggregate_results(result, bom_result)

        if "dimension" in standards:
            logger.info("Running dimension validation...")
            dim_result = self.dimension.validate(extraction)
            result.dimension_results = self.dimension.to_dict(dim_result)
            self._aggregate_results(result, dim_result)

        if "completeness" in standards:
            logger.info("Running completeness validation...")
            comp_result = self.completeness.validate(extraction)
            result.completeness_results = self.completeness.to_dict(comp_result)
            self._aggregate_results(result, comp_result)

        # Phase 26 - HPC Standards validation
        if "hpc_mechanical" in standards:
            logger.info("Running HPC mechanical validation...")
            hpc_mech_result = self.hpc_mechanical.validate(extraction)
            result.hpc_mechanical_results = self.hpc_mechanical.to_dict(hpc_mech_result)
            self._aggregate_results(result, hpc_mech_result)

        if "hpc_walkway" in standards:
            logger.info("Running HPC walkway validation...")
            hpc_walk_result = self.hpc_walkway.validate(extraction)
            result.hpc_walkway_results = self.hpc_walkway.to_dict(hpc_walk_result)
            self._aggregate_results(result, hpc_walk_result)

        if "hpc_header" in standards:
            logger.info("Running HPC header validation...")
            hpc_header_result = self.hpc_header.validate(extraction)
            result.hpc_header_results = self.hpc_header.to_dict(hpc_header_result)
            self._aggregate_results(result, hpc_header_result)

        # Calculate pass rate
        if result.total_checks > 0:
            result.pass_rate = (result.passed / result.total_checks) * 100

        # Count by severity
        result.severity_counts = {
            "critical": result.critical_failures,
            "error": result.failed,
            "warning": result.warnings,
            "info": result.passed,
        }

        result.duration_ms = int((time.time() - start_time) * 1000)

        logger.info(f"Validation complete: {result.total_checks} checks, {result.pass_rate:.1f}% passed")

        return result

    def _aggregate_results(self, result: PDFValidationResult, validation_result):
        """Aggregate validation results into the main result."""
        result.total_checks += validation_result.total_checks
        result.passed += validation_result.passed
        result.failed += validation_result.failed
        result.warnings += validation_result.warnings
        result.critical_failures += validation_result.critical_failures

        # Add issues
        for issue in validation_result.issues:
            result.all_issues.append({
                "severity": issue.severity.value,
                "check_type": issue.check_type,
                "message": issue.message,
                "location": issue.location,
                "suggestion": issue.suggestion,
                "standard_reference": issue.standard_reference,
            })

    def to_dict(self, result: PDFValidationResult) -> Dict[str, Any]:
        """Convert validation result to dictionary for JSON serialization."""
        return {
            "id": result.id,
            "file_path": result.file_path,
            "file_name": result.file_name,
            "timestamp": result.timestamp,
            "duration_ms": result.duration_ms,
            "drawing_type": result.drawing_type,
            "extraction": {
                "success": result.extraction_success,
                "errors": result.extraction_errors,
                "page_count": result.page_count,
                "part_number": result.part_number,
                "revision": result.revision,
            },
            "summary": {
                "total_checks": result.total_checks,
                "passed": result.passed,
                "failed": result.failed,
                "warnings": result.warnings,
                "critical_failures": result.critical_failures,
                "pass_rate": round(result.pass_rate, 1),
            },
            "severity_counts": result.severity_counts,
            "results_by_standard": {
                "api_661": result.api_661_results,
                "asme": result.asme_results,
                "aws_d1_1": result.aws_d1_1_results,
                "osha": result.osha_results,
                "bom": result.bom_results,
                "dimension": result.dimension_results,
                "completeness": result.completeness_results,
                "hpc_mechanical": result.hpc_mechanical_results,
                "hpc_walkway": result.hpc_walkway_results,
                "hpc_header": result.hpc_header_results,
            },
            "all_issues": result.all_issues,
        }

    def generate_report_summary(self, result: PDFValidationResult) -> str:
        """Generate a text summary of the validation results."""
        lines = [
            "=" * 60,
            "PDF DRAWING VALIDATION REPORT",
            "=" * 60,
            "",
            f"File: {result.file_name}",
            f"Part #: {result.part_number}",
            f"Revision: {result.revision}",
            f"Drawing Type: {result.drawing_type}",
            f"Pages: {result.page_count}",
            f"Validated: {result.timestamp}",
            "",
            "-" * 60,
            "SUMMARY",
            "-" * 60,
            f"Total Checks: {result.total_checks}",
            f"Passed: {result.passed} ({result.pass_rate:.1f}%)",
            f"Failed: {result.failed}",
            f"Warnings: {result.warnings}",
            f"Critical: {result.critical_failures}",
            "",
        ]

        if result.critical_failures > 0:
            lines.append("-" * 60)
            lines.append("CRITICAL ISSUES")
            lines.append("-" * 60)
            for issue in result.all_issues:
                if issue["severity"] == "critical":
                    lines.append(f"  [CRITICAL] {issue['message']}")
                    if issue.get("suggestion"):
                        lines.append(f"    Suggestion: {issue['suggestion']}")
            lines.append("")

        if result.failed > 0:
            lines.append("-" * 60)
            lines.append("ERRORS")
            lines.append("-" * 60)
            for issue in result.all_issues:
                if issue["severity"] == "error":
                    lines.append(f"  [ERROR] {issue['message']}")
            lines.append("")

        if result.warnings > 0:
            lines.append("-" * 60)
            lines.append("WARNINGS")
            lines.append("-" * 60)
            for issue in result.all_issues:
                if issue["severity"] == "warning":
                    lines.append(f"  [WARNING] {issue['message']}")
            lines.append("")

        lines.append("=" * 60)
        lines.append(f"Validation completed in {result.duration_ms}ms")
        lines.append("=" * 60)

        return "\n".join(lines)


# Convenience function for direct usage
def validate_pdf(
    pdf_path: str,
    standards: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Validate a PDF drawing and return results as dictionary.

    Args:
        pdf_path: Path to the PDF file
        standards: List of standards to check (default: all)

    Returns:
        Dictionary with validation results
    """
    engine = PDFValidationEngine()
    result = engine.validate(pdf_path, standards)
    return engine.to_dict(result)
