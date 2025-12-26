"""
Validation Orchestrator

Coordinates all CAD validation checks and generates comprehensive reports.
"""

import logging
import time
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .validation_models import (
    ACHEValidationResult,
    GDTValidationResult,
    MaterialValidationResult,
    ValidationIssue,
    ValidationProgress,
    ValidationReport,
    ValidationRequest,
    ValidationSeverity,
    ValidationStatus,
    WeldValidationResult,
)

# Import validators with graceful fallback
try:
    from ..adapters.gdt_parser import GDTParser
except ImportError:
    logging.warning("GDTParser not available")
    GDTParser = None

try:
    from ..adapters.welding_validator import WeldingValidator
except ImportError:
    logging.warning("WeldingValidator not available")
    WeldingValidator = None

try:
    from ..adapters.material_validator import MaterialValidator
except ImportError:
    logging.warning("MaterialValidator not available")
    MaterialValidator = None

try:
    from ..adapters.ache_validator import ACHEValidator
except ImportError:
    logging.warning("ACHEValidator not available")
    ACHEValidator = None

from .drawing_analyzer import DrawingAnalyzer

# Import new DrawingParser for validation
try:
    from ..drawing_parser import DrawingParser, get_drawing_parser
except ImportError:
    logging.warning("DrawingParser not available")
    DrawingParser = None
    get_drawing_parser = None

# Import BOM Manager
try:
    from ..bom_manager import BOMManager, get_bom_manager
except ImportError:
    logging.warning("BOMManager not available")
    BOMManager = None
    get_bom_manager = None

# Phase 25 - New validators
try:
    from .aisc_hole_validator import AISCHoleValidator
except ImportError:
    logging.warning("AISCHoleValidator not available")
    AISCHoleValidator = None

try:
    from .structural_capacity_validator import StructuralCapacityValidator
except ImportError:
    logging.warning("StructuralCapacityValidator not available")
    StructuralCapacityValidator = None

try:
    from .shaft_validator import ShaftValidator
except ImportError:
    logging.warning("ShaftValidator not available")
    ShaftValidator = None

try:
    from .handling_validator import HandlingValidator
except ImportError:
    logging.warning("HandlingValidator not available")
    HandlingValidator = None

try:
    from .bom_validator import BOMValidator
except ImportError:
    logging.warning("BOMValidator not available")
    BOMValidator = None

try:
    from .dimension_validator import DimensionValidator
except ImportError:
    logging.warning("DimensionValidator not available")
    DimensionValidator = None

try:
    from .osha_validator import OSHAValidator
except ImportError:
    logging.warning("OSHAValidator not available")
    OSHAValidator = None

# Phase 25.3-25.13 - New validators
try:
    from .fabrication_feasibility_validator import FabricationFeasibilityValidator
except ImportError:
    logging.warning("FabricationFeasibilityValidator not available")
    FabricationFeasibilityValidator = None

try:
    from .inspection_qc_validator import InspectionQCValidator
except ImportError:
    logging.warning("InspectionQCValidator not available")
    InspectionQCValidator = None

try:
    from .cross_part_validator import CrossPartValidator
except ImportError:
    logging.warning("CrossPartValidator not available")
    CrossPartValidator = None

try:
    from .materials_finishing_validator import MaterialsFinishingValidator
except ImportError:
    logging.warning("MaterialsFinishingValidator not available")
    MaterialsFinishingValidator = None

try:
    from .fastener_validator import FastenerValidator
except ImportError:
    logging.warning("FastenerValidator not available")
    FastenerValidator = None

try:
    from .rigging_validator import RiggingValidator
except ImportError:
    logging.warning("RiggingValidator not available")
    RiggingValidator = None

try:
    from .documentation_validator import DocumentationValidator
except ImportError:
    logging.warning("DocumentationValidator not available")
    DocumentationValidator = None

try:
    from .report_generator import ReportGenerator
except ImportError:
    logging.warning("ReportGenerator not available")
    ReportGenerator = None

logger = logging.getLogger(__name__)


class ValidationOrchestrator:
    """
    Orchestrates all validation checks.

    Coordinates GDT parsing, welding validation, material validation,
    and ACHE comprehensive checks. Generates unified validation reports.

    Example:
        >>> orchestrator = ValidationOrchestrator()
        >>> request = ValidationRequest(
        ...     type="drawing",
        ...     file_path="/path/to/drawing.pdf",
        ...     checks=["gdt", "welding"],
        ...     user_id="user123"
        ... )
        >>> report = await orchestrator.validate(request)
        >>> print(f"Pass rate: {report.pass_rate:.1f}%")
    """

    def __init__(self):
        """Initialize orchestrator with all validators."""
        self.gdt_parser = GDTParser() if GDTParser else None
        self.welding_validator = WeldingValidator() if WeldingValidator else None
        self.material_validator = MaterialValidator() if MaterialValidator else None
        self.ache_validator = ACHEValidator() if ACHEValidator else None
        self.drawing_analyzer = DrawingAnalyzer()
        self.drawing_parser = get_drawing_parser() if get_drawing_parser else None

        # Phase 25 - New validators
        self.aisc_hole_validator = AISCHoleValidator() if AISCHoleValidator else None
        self.structural_validator = StructuralCapacityValidator() if StructuralCapacityValidator else None
        self.shaft_validator = ShaftValidator() if ShaftValidator else None
        self.handling_validator = HandlingValidator() if HandlingValidator else None
        self.bom_validator = BOMValidator() if BOMValidator else None
        self.dimension_validator = DimensionValidator() if DimensionValidator else None
        self.osha_validator = OSHAValidator() if OSHAValidator else None

        # Phase 25.3-25.13 - Additional validators
        self.fabrication_validator = FabricationFeasibilityValidator() if FabricationFeasibilityValidator else None
        self.inspection_validator = InspectionQCValidator() if InspectionQCValidator else None
        self.cross_part_validator = CrossPartValidator() if CrossPartValidator else None
        self.materials_validator = MaterialsFinishingValidator() if MaterialsFinishingValidator else None
        self.fastener_validator = FastenerValidator() if FastenerValidator else None
        self.rigging_validator = RiggingValidator() if RiggingValidator else None
        self.documentation_validator = DocumentationValidator() if DocumentationValidator else None
        self.report_generator = ReportGenerator() if ReportGenerator else None

        try:
            from core.flatter_files_client import FlatterFilesClient

            self.flatter_files_client = FlatterFilesClient()
        except (ImportError, ValueError):
            self.flatter_files_client = None

        # Progress callbacks
        self._progress_callbacks: List[Callable[[ValidationProgress], None]] = []

        logger.info("ValidationOrchestrator initialized")
        logger.info(f"  GDT Parser: {'✓' if self.gdt_parser else '✗'}")
        logger.info(f"  Welding Validator: {'✓' if self.welding_validator else '✗'}")
        logger.info(f"  Material Validator: {'✓' if self.material_validator else '✗'}")
        logger.info(f"  ACHE Validator: {'✓' if self.ache_validator else '✗'}")
        logger.info(f"  Drawing Parser: {'✓' if self.drawing_parser else '✗'}")
        logger.info(f"  AISC Hole Validator: {'✓' if self.aisc_hole_validator else '✗'}")
        logger.info(f"  Structural Validator: {'✓' if self.structural_validator else '✗'}")
        logger.info(f"  Shaft Validator: {'✓' if self.shaft_validator else '✗'}")
        logger.info(f"  Handling Validator: {'✓' if self.handling_validator else '✗'}")
        logger.info(f"  BOM Validator: {'✓' if self.bom_validator else '✗'}")
        logger.info(f"  Dimension Validator: {'✓' if self.dimension_validator else '✗'}")
        logger.info(f"  OSHA Validator: {'✓' if self.osha_validator else '✗'}")
        logger.info(
            f"  Flatter Files Client: {'✓' if self.flatter_files_client else '✗'}"
        )

    def register_progress_callback(
        self, callback: Callable[[ValidationProgress], None]
    ) -> None:
        """Register a callback for progress updates."""
        self._progress_callbacks.append(callback)

    def _report_progress(
        self,
        request_id: str,
        status: ValidationStatus,
        step: str,
        progress: int,
        message: str = "",
    ) -> None:
        """Report progress to all registered callbacks."""
        progress_update = ValidationProgress(
            request_id=request_id,
            status=status,
            current_step=step,
            progress_percent=progress,
            message=message,
        )

        for callback in self._progress_callbacks:
            try:
                callback(progress_update)
            except Exception as e:
                logger.error(f"Progress callback failed: {e}")

    async def validate(self, request: ValidationRequest) -> ValidationReport:
        """
        Run all requested validation checks.

        Args:
            request: Validation request with file and check types

        Returns:
            Complete validation report with all results
        """
        start_time = time.time()
        request_id = str(uuid.uuid4())

        # Determine file path
        file_path = request.file_path or await self._resolve_file_id(request.file_id)
        if not file_path:
            raise ValueError("Either file_path or file_id must be provided")

        logger.info(f"Starting validation {request_id} for {file_path}")
        logger.info(f"  Checks requested: {request.checks}")

        # Create initial report
        report = ValidationReport(
            id=str(uuid.uuid4()),
            request_id=request_id,
            duration_ms=0,
            input_file=file_path,
            status=ValidationStatus.RUNNING,
        )

        try:
            # Step 1: Analyze drawing (10%)
            self._report_progress(
                request_id,
                ValidationStatus.RUNNING,
                "Analyzing drawing",
                10,
                "Extracting text and metadata from PDF...",
            )

            analysis = self.drawing_analyzer.analyze_pdf(file_path)

            # Step 2: Run requested checks
            checks_to_run = self._determine_checks(request.checks)
            total_checks = len(checks_to_run)

            for i, check in enumerate(checks_to_run):
                progress = 10 + int((i + 1) / total_checks * 80)

                if check == "gdt":
                    self._report_progress(
                        request_id,
                        ValidationStatus.RUNNING,
                        "GD&T validation",
                        progress,
                        "Parsing geometric tolerances...",
                    )
                    report.gdt_results = await self._validate_gdt(analysis)

                elif check == "welding":
                    self._report_progress(
                        request_id,
                        ValidationStatus.RUNNING,
                        "Welding validation",
                        progress,
                        "Validating weld symbols and callouts...",
                    )
                    report.welding_results = await self._validate_welding(analysis)

                elif check == "material":
                    self._report_progress(
                        request_id,
                        ValidationStatus.RUNNING,
                        "Material validation",
                        progress,
                        "Checking material specifications...",
                    )
                    report.material_results = await self._validate_material(analysis)

                elif check == "ache":
                    self._report_progress(
                        request_id,
                        ValidationStatus.RUNNING,
                        "ACHE validation",
                        progress,
                        "Running 130-point comprehensive checklist...",
                    )
                    report.ache_results = await self._validate_ache(analysis, file_path)

                elif check == "drawing":
                    self._report_progress(
                        request_id,
                        ValidationStatus.RUNNING,
                        "Drawing validation",
                        progress,
                        "Validating title block, dimensions, and notes...",
                    )
                    report.drawing_results = await self._validate_drawing(file_path)

                # Phase 25 - New validators
                elif check == "holes":
                    self._report_progress(
                        request_id,
                        ValidationStatus.RUNNING,
                        "AISC Hole validation",
                        progress,
                        "Checking hole edge distances and spacing...",
                    )
                    report.phase25_results = report.phase25_results or {}
                    report.phase25_results["holes"] = await self._validate_holes(analysis)

                elif check == "structural":
                    self._report_progress(
                        request_id,
                        ValidationStatus.RUNNING,
                        "Structural capacity validation",
                        progress,
                        "Checking bolt and weld capacities...",
                    )
                    report.phase25_results = report.phase25_results or {}
                    report.phase25_results["structural"] = await self._validate_structural(analysis)

                elif check == "shaft":
                    self._report_progress(
                        request_id,
                        ValidationStatus.RUNNING,
                        "Shaft/machining validation",
                        progress,
                        "Checking tolerances and keyways...",
                    )
                    report.phase25_results = report.phase25_results or {}
                    report.phase25_results["shaft"] = await self._validate_shaft(analysis)

                elif check == "handling":
                    self._report_progress(
                        request_id,
                        ValidationStatus.RUNNING,
                        "Handling validation",
                        progress,
                        "Checking lifting lugs and CG...",
                    )
                    report.phase25_results = report.phase25_results or {}
                    report.phase25_results["handling"] = await self._validate_handling(analysis)

                elif check == "bom":
                    self._report_progress(
                        request_id,
                        ValidationStatus.RUNNING,
                        "BOM validation",
                        progress,
                        "Validating bill of materials...",
                    )
                    report.phase25_results = report.phase25_results or {}
                    report.phase25_results["bom"] = await self._validate_bom(analysis)

                elif check == "dimensions":
                    self._report_progress(
                        request_id,
                        ValidationStatus.RUNNING,
                        "Dimension validation",
                        progress,
                        "Checking dimension callouts...",
                    )
                    report.phase25_results = report.phase25_results or {}
                    report.phase25_results["dimensions"] = await self._validate_dimensions(analysis)

                elif check == "osha":
                    self._report_progress(
                        request_id,
                        ValidationStatus.RUNNING,
                        "OSHA safety validation",
                        progress,
                        "Checking safety requirements...",
                    )
                    report.phase25_results = report.phase25_results or {}
                    report.phase25_results["osha"] = await self._validate_osha(analysis)

            # Step 3: Calculate summary (95%)
            self._report_progress(
                request_id,
                ValidationStatus.RUNNING,
                "Generating report",
                95,
                "Calculating summary statistics...",
            )

            report.calculate_summary()

            # Complete
            report.status = ValidationStatus.COMPLETE
            duration_ms = int((time.time() - start_time) * 1000)
            report.duration_ms = duration_ms

            self._report_progress(
                request_id,
                ValidationStatus.COMPLETE,
                "Complete",
                100,
                f"Validation complete in {duration_ms}ms",
            )

            logger.info(f"Validation {request_id} complete:")
            logger.info(f"  Duration: {duration_ms}ms")
            logger.info(f"  Total checks: {report.total_checks}")
            logger.info(f"  Pass rate: {report.pass_rate:.1f}%")
            logger.info(f"  Issues: {len(report.all_issues)}")

            return report

        except Exception as e:
            logger.error(f"Validation {request_id} failed: {e}", exc_info=True)
            report.status = ValidationStatus.ERROR
            report.duration_ms = int((time.time() - start_time) * 1000)

            self._report_progress(
                request_id,
                ValidationStatus.ERROR,
                "Error",
                100,
                f"Validation failed: {str(e)}",
            )

            raise

    def _determine_checks(self, requested: List[str]) -> List[str]:
        """Determine which checks to run based on request."""
        if "all" in requested:
            checks = []
            if self.gdt_parser:
                checks.append("gdt")
            if self.welding_validator:
                checks.append("welding")
            if self.material_validator:
                checks.append("material")
            if self.ache_validator:
                checks.append("ache")
            if self.drawing_parser:
                checks.append("drawing")
            # Phase 25 validators
            if self.aisc_hole_validator:
                checks.append("holes")
            if self.structural_validator:
                checks.append("structural")
            if self.shaft_validator:
                checks.append("shaft")
            if self.handling_validator:
                checks.append("handling")
            if self.bom_validator:
                checks.append("bom")
            if self.dimension_validator:
                checks.append("dimensions")
            if self.osha_validator:
                checks.append("osha")
            return checks
        else:
            return [c for c in requested if self._is_check_available(c)]

    def _is_check_available(self, check: str) -> bool:
        """Check if a validator is available."""
        if check == "gdt":
            return self.gdt_parser is not None
        elif check == "welding":
            return self.welding_validator is not None
        elif check == "material":
            return self.material_validator is not None
        elif check == "ache":
            return self.ache_validator is not None
        elif check == "drawing":
            return self.drawing_parser is not None
        # Phase 25 validators
        elif check == "holes":
            return self.aisc_hole_validator is not None
        elif check == "structural":
            return self.structural_validator is not None
        elif check == "shaft":
            return self.shaft_validator is not None
        elif check == "handling":
            return self.handling_validator is not None
        elif check == "bom":
            return self.bom_validator is not None
        elif check == "dimensions":
            return self.dimension_validator is not None
        elif check == "osha":
            return self.osha_validator is not None
        return False

    async def _validate_gdt(self, analysis: Any) -> GDTValidationResult:
        """Run GD&T validation."""
        if not self.gdt_parser:
            return GDTValidationResult()

        try:
            # Parse GD&T features from extracted text
            features = self.gdt_parser.parse_drawing_text(analysis.extracted_text)

            issues = []
            valid_count = 0

            for feature in features:
                if feature.get("valid", True):
                    valid_count += 1
                else:
                    issues.append(
                        ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            check_type="gdt",
                            message=feature.get("error", "Invalid GD&T feature"),
                            location=feature.get("location"),
                            standard_reference="ASME Y14.5-2018",
                        )
                    )

            return GDTValidationResult(
                total_features=len(features),
                valid_features=valid_count,
                invalid_features=len(features) - valid_count,
                issues=issues,
                datums_found=analysis.datums if hasattr(analysis, "datums") else [],
                tolerances_parsed=len(features),
            )

        except Exception as e:
            logger.error(f"GDT validation failed: {e}")
            return GDTValidationResult(
                issues=[
                    ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        check_type="gdt",
                        message=f"GDT validation error: {str(e)}",
                    )
                ]
            )

    async def _validate_welding(self, analysis: Any) -> WeldValidationResult:
        """Run welding validation."""
        if not self.welding_validator:
            return WeldValidationResult()

        try:
            # Extract weld callouts from analysis
            weld_callouts = (
                analysis.weld_callouts if hasattr(analysis, "weld_callouts") else []
            )

            issues = []
            compliant_count = 0

            for callout in weld_callouts:
                result = self.welding_validator.validate_weld_symbol(callout)

                if result.get("compliant", False):
                    compliant_count += 1
                else:
                    issues.append(
                        ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            check_type="welding",
                            message=result.get("message", "Non-compliant weld"),
                            location=callout.get("location"),
                            standard_reference="AWS D1.1",
                        )
                    )

            return WeldValidationResult(
                total_welds=len(weld_callouts),
                compliant_welds=compliant_count,
                non_compliant_welds=len(weld_callouts) - compliant_count,
                issues=issues,
                aws_d11_compliant=len(issues) == 0,
                weld_symbols_found=[c.get("symbol", "") for c in weld_callouts],
            )

        except Exception as e:
            logger.error(f"Welding validation failed: {e}")
            return WeldValidationResult(
                issues=[
                    ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        check_type="welding",
                        message=f"Welding validation error: {str(e)}",
                    )
                ]
            )

    async def _validate_material(self, analysis: Any) -> MaterialValidationResult:
        """Run material validation."""
        if not self.material_validator:
            return MaterialValidationResult()

        try:
            # Extract material specs from analysis
            material_specs = (
                analysis.materials if hasattr(analysis, "materials") else []
            )

            issues = []
            compliant_count = 0
            astm_specs = []

            for spec in material_specs:
                result = self.material_validator.validate_material_spec(spec)

                if result.get("compliant", False):
                    compliant_count += 1

                if "astm_spec" in spec:
                    astm_specs.append(spec["astm_spec"])

                for warning in result.get("warnings", []):
                    issues.append(
                        ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            check_type="material",
                            message=warning,
                            standard_reference=spec.get("astm_spec"),
                        )
                    )

            return MaterialValidationResult(
                materials_validated=len(material_specs),
                mtrs_found=len(material_specs),
                compliant_materials=compliant_count,
                issues=issues,
                astm_specs_checked=astm_specs,
                carbon_equivalent_ok=all(
                    i.severity != ValidationSeverity.CRITICAL for i in issues
                ),
            )

        except Exception as e:
            logger.error(f"Material validation failed: {e}")
            return MaterialValidationResult(
                issues=[
                    ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        check_type="material",
                        message=f"Material validation error: {str(e)}",
                    )
                ]
            )

    async def _validate_ache(
        self, analysis: Any, file_path: str
    ) -> ACHEValidationResult:
        """Run ACHE 130-point validation."""
        if not self.ache_validator:
            return ACHEValidationResult()

        try:
            # Run comprehensive ACHE validation
            result = self.ache_validator.validate_complete_drawing(
                file_path, analysis.__dict__ if hasattr(analysis, "__dict__") else {}
            )

            # Convert ACHE results to standard format
            issues = []
            for check in result.get("checks", []):
                if not check.get("passed", True):
                    severity = (
                        ValidationSeverity.CRITICAL
                        if check.get("critical", False)
                        else ValidationSeverity.WARNING
                    )

                    issues.append(
                        ValidationIssue(
                            severity=severity,
                            check_type="ache",
                            message=check.get("message", "ACHE check failed"),
                            location=check.get("section"),
                            suggestion=check.get("recommendation"),
                            standard_reference=check.get("standard"),
                        )
                    )

            return ACHEValidationResult(
                total_checks=result.get("total_checks", 130),
                passed=result.get("passed", 0),
                warnings=result.get("warnings", 0),
                errors=result.get("errors", 0),
                critical_failures=result.get("critical_failures", 0),
                issues=issues,
                category_scores=result.get("category_scores", {}),
            )

        except Exception as e:
            logger.error(f"ACHE validation failed: {e}")
            return ACHEValidationResult(
                issues=[
                    ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        check_type="ache",
                        message=f"ACHE validation error: {str(e)}",
                    )
                ]
            )

    async def _validate_drawing(self, file_path: str) -> Dict[str, Any]:
        """
        Run drawing validation using DrawingParser.

        Validates:
        - Title block metadata (part number, revision, date)
        - Dimensions extraction
        - Notes and BOM extraction
        """
        if not self.drawing_parser:
            return {"error": "DrawingParser not available"}

        try:
            # Parse the drawing
            drawing_data = self.drawing_parser.parse_file(file_path)

            issues = []

            # Check for missing metadata
            if not drawing_data.metadata.part_number:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        check_type="drawing",
                        message="Part number not found in title block",
                        suggestion="Ensure title block contains PART NO or DWG NO",
                    )
                )

            if not drawing_data.metadata.revision:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        check_type="drawing",
                        message="Revision not found in title block",
                        suggestion="Ensure title block contains REV field",
                    )
                )

            if not drawing_data.metadata.material:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        check_type="drawing",
                        message="Material specification not found",
                        suggestion="Add material callout (e.g., SA-516-70, ASTM A36)",
                    )
                )

            # Check for dimensions
            if len(drawing_data.dimensions) == 0:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        check_type="drawing",
                        message="No dimensions extracted from drawing",
                        suggestion="Check if drawing has readable dimension text",
                    )
                )

            # Check for notes
            if len(drawing_data.notes) == 0:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        check_type="drawing",
                        message="No notes found in drawing",
                    )
                )

            # Report any parse errors
            for error in drawing_data.errors:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        check_type="drawing",
                        message=f"Parse error: {error}",
                    )
                )

            return {
                "total_checks": 5,
                "passed": 5
                - len(
                    [
                        i
                        for i in issues
                        if i.severity
                        in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]
                    ]
                ),
                "warnings": len(
                    [i for i in issues if i.severity == ValidationSeverity.WARNING]
                ),
                "errors": len(
                    [i for i in issues if i.severity == ValidationSeverity.ERROR]
                ),
                "issues": issues,
                "metadata": {
                    "part_number": drawing_data.metadata.part_number,
                    "revision": drawing_data.metadata.revision,
                    "material": drawing_data.metadata.material,
                    "title": drawing_data.metadata.title,
                    "date": drawing_data.metadata.date,
                },
                "dimensions_count": len(drawing_data.dimensions),
                "notes_count": len(drawing_data.notes),
                "bom_items": len(drawing_data.bom),
                "layers": drawing_data.layers,
            }

        except Exception as e:
            logger.error(f"Drawing validation failed: {e}")
            return {
                "error": str(e),
                "issues": [
                    ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        check_type="drawing",
                        message=f"Drawing validation error: {str(e)}",
                    )
                ],
            }

    async def _resolve_file_id(self, file_id: Optional[str]) -> Optional[str]:
        """Resolve Flatter Files ID to local path."""
        if not file_id:
            return None

        if self.flatter_files_client:
            import tempfile
            import os

            download_path = os.path.join(tempfile.gettempdir(), file_id)
            if await self.flatter_files_client.download_file(file_id, download_path):
                return download_path
            else:
                return None

        # For now, assume file_id is already a path if client is not available
        return file_id

    # Phase 25 - New validation methods

    async def _validate_holes(self, analysis: Any) -> Dict[str, Any]:
        """Run AISC hole validation."""
        if not self.aisc_hole_validator:
            return {"error": "AISCHoleValidator not available"}

        try:
            from .aisc_hole_validator import HoleData

            # Extract hole data from analysis
            holes = []
            if hasattr(analysis, "holes"):
                for h in analysis.holes:
                    holes.append(HoleData(
                        diameter=h.get("diameter", 0.75),
                        edge_distance=h.get("edge_distance"),
                        spacing=h.get("spacing"),
                        bolt_diameter=h.get("bolt_diameter", h.get("diameter", 0.75) - 0.0625),
                    ))

            if not holes:
                return {
                    "total_checks": 0,
                    "passed": 0,
                    "message": "No holes found in drawing analysis",
                }

            result = self.aisc_hole_validator.validate_holes(holes)
            return self.aisc_hole_validator.to_dict(result)

        except Exception as e:
            logger.error(f"Hole validation failed: {e}")
            return {"error": str(e)}

    async def _validate_structural(self, analysis: Any) -> Dict[str, Any]:
        """Run structural capacity validation."""
        if not self.structural_validator:
            return {"error": "StructuralCapacityValidator not available"}

        try:
            results = {"checks": []}

            # Check bolt connections if present
            if hasattr(analysis, "bolts"):
                from .structural_capacity_validator import BoltData
                for b in analysis.bolts:
                    bolt = BoltData(
                        diameter=b.get("diameter", 0.75),
                        grade=b.get("grade", "A325"),
                        num_bolts=b.get("count", 1),
                    )
                    result = self.structural_validator.check_bolt_shear(
                        bolt, b.get("load_kips")
                    )
                    results["checks"].append(self.structural_validator.to_dict(result))

            # Check welds if present
            if hasattr(analysis, "welds"):
                from .structural_capacity_validator import WeldData
                for w in analysis.welds:
                    weld = WeldData(
                        leg_size=w.get("size", 0.25),
                        length=w.get("length", 1.0),
                    )
                    result = self.structural_validator.check_fillet_weld(
                        weld, w.get("thickness", 0.5), w.get("load_kips")
                    )
                    results["checks"].append(self.structural_validator.to_dict(result))

            return results

        except Exception as e:
            logger.error(f"Structural validation failed: {e}")
            return {"error": str(e)}

    async def _validate_shaft(self, analysis: Any) -> Dict[str, Any]:
        """Run shaft/machining validation."""
        if not self.shaft_validator:
            return {"error": "ShaftValidator not available"}

        try:
            results = {"checks": []}

            if hasattr(analysis, "shafts"):
                from .shaft_validator import ShaftData
                for s in analysis.shafts:
                    shaft = ShaftData(
                        diameter=s.get("diameter", 1.0),
                        tolerance_plus=s.get("tolerance_plus"),
                        tolerance_minus=s.get("tolerance_minus"),
                        surface_finish_ra=s.get("surface_finish"),
                        runout_tir=s.get("runout"),
                    )
                    feature_type = s.get("feature_type", "general")
                    result = self.shaft_validator.validate_shaft(shaft, feature_type)
                    results["checks"].append(self.shaft_validator.to_dict(result))

            if hasattr(analysis, "keyways"):
                from .shaft_validator import KeywayData
                for k in analysis.keyways:
                    keyway = KeywayData(
                        width=k.get("width", 0.25),
                        depth=k.get("depth", 0.125),
                        angular_location=k.get("angular_location"),
                    )
                    result = self.shaft_validator.validate_keyway(
                        keyway, k.get("shaft_diameter", 1.0)
                    )
                    results["checks"].append(self.shaft_validator.to_dict(result))

            return results

        except Exception as e:
            logger.error(f"Shaft validation failed: {e}")
            return {"error": str(e)}

    async def _validate_handling(self, analysis: Any) -> Dict[str, Any]:
        """Run handling/lifting validation."""
        if not self.handling_validator:
            return {"error": "HandlingValidator not available"}

        try:
            from .handling_validator import HandlingData

            # Get weight from analysis or estimate
            weight = 0.0
            if hasattr(analysis, "weight_lbs"):
                weight = analysis.weight_lbs
            elif hasattr(analysis, "estimated_weight"):
                weight = analysis.estimated_weight

            handling = HandlingData(
                total_weight_lbs=weight,
                length_in=getattr(analysis, "length_in", None),
                width_in=getattr(analysis, "width_in", None),
                height_in=getattr(analysis, "height_in", None),
                has_lifting_lugs=getattr(analysis, "has_lifting_lugs", False),
                num_lifting_lugs=getattr(analysis, "num_lifting_lugs", 0),
                lug_capacity_lbs=getattr(analysis, "lug_capacity_lbs", None),
                cg_marked=getattr(analysis, "cg_marked", False),
                cg_location=getattr(analysis, "cg_location", None),
                has_rigging_diagram=getattr(analysis, "has_rigging_diagram", False),
            )

            result = self.handling_validator.validate(handling)
            return self.handling_validator.to_dict(result)

        except Exception as e:
            logger.error(f"Handling validation failed: {e}")
            return {"error": str(e)}

    async def _validate_bom(self, analysis: Any) -> Dict[str, Any]:
        """Run BOM validation."""
        if not self.bom_validator:
            return {"error": "BOMValidator not available"}

        try:
            bom_items = []
            if hasattr(analysis, "bom"):
                bom_items = analysis.bom

            result = self.bom_validator.validate(bom_items)
            return self.bom_validator.to_dict(result)

        except Exception as e:
            logger.error(f"BOM validation failed: {e}")
            return {"error": str(e)}

    async def _validate_dimensions(self, analysis: Any) -> Dict[str, Any]:
        """Run dimension validation."""
        if not self.dimension_validator:
            return {"error": "DimensionValidator not available"}

        try:
            dimensions = []
            if hasattr(analysis, "dimensions"):
                dimensions = analysis.dimensions

            result = self.dimension_validator.validate(dimensions)
            return self.dimension_validator.to_dict(result)

        except Exception as e:
            logger.error(f"Dimension validation failed: {e}")
            return {"error": str(e)}

    async def _validate_osha(self, analysis: Any) -> Dict[str, Any]:
        """Run OSHA safety validation."""
        if not self.osha_validator:
            return {"error": "OSHAValidator not available"}

        try:
            # Extract safety-related data from analysis
            safety_data = {}
            if hasattr(analysis, "guardrails"):
                safety_data["guardrails"] = analysis.guardrails
            if hasattr(analysis, "ladders"):
                safety_data["ladders"] = analysis.ladders
            if hasattr(analysis, "platforms"):
                safety_data["platforms"] = analysis.platforms

            result = self.osha_validator.validate(safety_data)
            return self.osha_validator.to_dict(result)

        except Exception as e:
            logger.error(f"OSHA validation failed: {e}")
            return {"error": str(e)}
