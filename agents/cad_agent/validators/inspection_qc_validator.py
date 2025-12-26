"""
Inspection & QC Validator
==========================
Validates inspection requirements, NDE callouts, and QC documentation.

Phase 25.9 - Inspection & Quality Control
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
from enum import Enum

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.inspection_qc")


class NDEMethod(str, Enum):
    """Non-Destructive Examination methods."""
    VT = "VT"    # Visual Testing
    PT = "PT"    # Penetrant Testing
    MT = "MT"    # Magnetic Particle Testing
    UT = "UT"    # Ultrasonic Testing
    RT = "RT"    # Radiographic Testing
    PAUT = "PAUT"  # Phased Array UT
    TOFD = "TOFD"  # Time of Flight Diffraction


class WeldCategory(str, Enum):
    """Weld categories requiring different inspection levels."""
    PRESSURE_RETAINING = "pressure_retaining"
    STRUCTURAL_PRIMARY = "structural_primary"
    STRUCTURAL_SECONDARY = "structural_secondary"
    ATTACHMENT = "attachment"
    SEAL = "seal"


# Minimum NDE requirements by weld category and code
NDE_REQUIREMENTS = {
    # (category, code): [required NDE methods]
    (WeldCategory.PRESSURE_RETAINING, "ASME_VIII"): [NDEMethod.RT, NDEMethod.VT],
    (WeldCategory.PRESSURE_RETAINING, "ASME_B31.3"): [NDEMethod.RT, NDEMethod.VT],
    (WeldCategory.STRUCTURAL_PRIMARY, "AWS_D1.1"): [NDEMethod.VT, NDEMethod.UT],
    (WeldCategory.STRUCTURAL_PRIMARY, "AISC"): [NDEMethod.VT],
    (WeldCategory.STRUCTURAL_SECONDARY, "AWS_D1.1"): [NDEMethod.VT],
    (WeldCategory.ATTACHMENT, "AWS_D1.1"): [NDEMethod.VT],
    (WeldCategory.SEAL, "ASME_VIII"): [NDEMethod.PT, NDEMethod.VT],
}

# NDE acceptance criteria references
NDE_ACCEPTANCE_CRITERIA = {
    NDEMethod.VT: "AWS D1.1 Table 6.1 / ASME VIII UW-35",
    NDEMethod.PT: "ASME V Article 6 / ASTM E1417",
    NDEMethod.MT: "ASME V Article 7 / ASTM E1444",
    NDEMethod.UT: "AWS D1.1 Annex S / ASME V Article 4",
    NDEMethod.RT: "AWS D1.1 Section 6 / ASME V Article 2",
}

# Required QC documentation by code
QC_DOCUMENTATION = {
    "ASME_VIII": [
        "U-1 Data Report",
        "MAWP Calculation",
        "Hydrostatic Test Report",
        "MTR (Mill Test Reports)",
        "WPS/PQR",
        "Welder Continuity Log",
        "NDE Reports",
        "PWHT Charts (if applicable)",
    ],
    "AWS_D1.1": [
        "WPS/PQR",
        "Welder Qualification Records",
        "NDE Reports",
        "Fit-up Inspection Records",
        "Final Visual Inspection Report",
    ],
    "API_661": [
        "Tube Bundle Data Sheet",
        "Fan Performance Test",
        "Hydrostatic Test Report",
        "MTR (Mill Test Reports)",
        "Coating Inspection Report",
    ],
    "AISC": [
        "Shop Drawings (approved)",
        "MTR (Mill Test Reports)",
        "Bolt Tensioning Records",
        "NDE Reports",
        "Dimensional Inspection Report",
    ],
}

# Dimensional inspection requirements
DIMENSIONAL_TOLERANCES = {
    "length": {"standard": 0.0625, "precision": 0.03125},  # inches
    "flatness": {"standard": 0.125, "precision": 0.0625},
    "squareness": {"standard": 0.0625, "precision": 0.03125},
    "hole_location": {"standard": 0.0625, "precision": 0.03125},
    "bolt_hole_diameter": {"standard": 0.0625, "precision": 0.03125},
}


@dataclass
class WeldInspectionData:
    """Data for weld inspection validation."""
    weld_id: str
    category: WeldCategory
    length_in: float
    size_in: float
    joint_type: str  # CJP, PJP, fillet
    code: str = "AWS_D1.1"
    specified_nde: List[NDEMethod] = field(default_factory=list)
    material: str = "carbon_steel"
    thickness_in: float = 0.5


@dataclass
class InspectionPlanData:
    """Complete inspection plan data."""
    part_number: str
    applicable_codes: List[str] = field(default_factory=list)
    welds: List[WeldInspectionData] = field(default_factory=list)
    critical_dimensions: List[Dict] = field(default_factory=list)
    surface_finish_requirements: List[Dict] = field(default_factory=list)
    coating_requirements: Optional[Dict] = None
    pressure_test_required: bool = False
    test_pressure_psig: Optional[float] = None
    mtr_required: bool = True
    pwht_required: bool = False


@dataclass
class InspectionValidationResult:
    """Inspection & QC validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

    # Statistics
    welds_checked: int = 0
    nde_requirements_missing: int = 0
    documentation_gaps: int = 0
    inspection_points: int = 0

    # Generated outputs
    inspection_plan: List[str] = field(default_factory=list)
    required_documentation: List[str] = field(default_factory=list)


class InspectionQCValidator:
    """
    Validates inspection requirements and QC documentation.

    Checks:
    1. NDE methods specified for each weld category
    2. NDE acceptance criteria referenced
    3. Required QC documentation listed
    4. Dimensional inspection points identified
    5. Surface finish and coating inspection
    6. Pressure/leak test requirements
    7. MTR requirements
    8. PWHT requirements and verification
    9. Witness points identified
    10. Final inspection checklist completeness
    """

    def __init__(self):
        pass

    def validate_inspection_plan(
        self,
        data: InspectionPlanData
    ) -> InspectionValidationResult:
        """
        Validate an inspection plan for completeness.

        Args:
            data: Inspection plan data

        Returns:
            InspectionValidationResult
        """
        result = InspectionValidationResult()
        result.welds_checked = len(data.welds)
        result.inspection_points = len(data.critical_dimensions)

        # Run checks
        self._check_nde_requirements(data, result)
        self._check_nde_acceptance_criteria(data, result)
        self._check_required_documentation(data, result)
        self._check_dimensional_inspection(data, result)
        self._check_surface_coating(data, result)
        self._check_pressure_test(data, result)
        self._check_mtr_requirements(data, result)
        self._check_pwht_requirements(data, result)
        self._check_witness_points(data, result)
        self._generate_inspection_checklist(data, result)

        return result

    def validate_weld_nde(
        self,
        welds: List[WeldInspectionData]
    ) -> InspectionValidationResult:
        """
        Validate NDE requirements for a list of welds.

        Args:
            welds: List of weld inspection data

        Returns:
            InspectionValidationResult
        """
        data = InspectionPlanData(
            part_number="",
            welds=welds,
            applicable_codes=list(set(w.code for w in welds))
        )
        return self.validate_inspection_plan(data)

    def _check_nde_requirements(
        self,
        data: InspectionPlanData,
        result: InspectionValidationResult
    ):
        """Check that required NDE methods are specified for each weld."""
        if not data.welds:
            return

        result.total_checks += 1

        for weld in data.welds:
            key = (weld.category, weld.code)
            required_nde = NDE_REQUIREMENTS.get(key, [NDEMethod.VT])

            missing_nde = []
            for method in required_nde:
                if method not in weld.specified_nde:
                    missing_nde.append(method)

            if missing_nde:
                result.nde_requirements_missing += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="nde_missing",
                    message=f"Weld {weld.weld_id}: Missing NDE - {', '.join(m.value for m in missing_nde)}",
                    location=f"Weld {weld.weld_id}",
                    suggestion=f"Add {', '.join(m.value for m in missing_nde)} per {weld.code}",
                    standard_reference=weld.code,
                ))

            # Check for CJP welds - require more extensive NDE
            if weld.joint_type.upper() == "CJP" and NDEMethod.UT not in weld.specified_nde and NDEMethod.RT not in weld.specified_nde:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="cjp_nde",
                    message=f"Weld {weld.weld_id}: CJP weld should have UT or RT",
                    location=f"Weld {weld.weld_id}",
                    suggestion="Consider adding UT or RT for complete joint penetration verification",
                ))
                result.warnings += 1

        if result.nde_requirements_missing == 0:
            result.passed += 1
        else:
            result.failed += 1

    def _check_nde_acceptance_criteria(
        self,
        data: InspectionPlanData,
        result: InspectionValidationResult
    ):
        """Check that NDE acceptance criteria are referenced."""
        result.total_checks += 1

        # Collect all NDE methods specified
        all_nde: Set[NDEMethod] = set()
        for weld in data.welds:
            all_nde.update(weld.specified_nde)

        if all_nde:
            # Add acceptance criteria to inspection plan
            for method in all_nde:
                criteria = NDE_ACCEPTANCE_CRITERIA.get(method, "Per applicable code")
                result.inspection_plan.append(f"{method.value}: {criteria}")

            result.passed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="nde_acceptance",
                message=f"NDE acceptance criteria for {len(all_nde)} methods",
                suggestion="Verify acceptance criteria referenced in NDE procedures",
            ))
        else:
            result.passed += 1

    def _check_required_documentation(
        self,
        data: InspectionPlanData,
        result: InspectionValidationResult
    ):
        """Check that required QC documentation is specified."""
        result.total_checks += 1

        for code in data.applicable_codes:
            required_docs = QC_DOCUMENTATION.get(code, [])
            result.required_documentation.extend(required_docs)

        # Remove duplicates
        result.required_documentation = list(set(result.required_documentation))

        if result.required_documentation:
            result.passed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="documentation_list",
                message=f"{len(result.required_documentation)} documentation items required",
                suggestion="Ensure all listed documentation is included in turnover package",
            ))
        else:
            result.warnings += 1
            result.documentation_gaps += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="no_documentation",
                message="No applicable codes specified for documentation requirements",
                suggestion="Specify applicable codes (ASME VIII, AWS D1.1, API 661, etc.)",
            ))

    def _check_dimensional_inspection(
        self,
        data: InspectionPlanData,
        result: InspectionValidationResult
    ):
        """Check dimensional inspection requirements."""
        result.total_checks += 1

        if data.critical_dimensions:
            result.passed += 1

            # Check for tolerance specifications
            for i, dim in enumerate(data.critical_dimensions):
                if "tolerance" not in dim and "plus_minus" not in dim:
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        check_type="dimension_tolerance",
                        message=f"Critical dimension #{i+1}: No tolerance specified",
                        location=f"Dimension {i+1}",
                        suggestion="Add tolerance for critical dimensions",
                    ))
                    result.warnings += 1
        else:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="no_critical_dimensions",
                message="No critical dimensions identified for inspection",
                suggestion="Identify key dimensions for dimensional inspection",
            ))
            result.passed += 1

    def _check_surface_coating(
        self,
        data: InspectionPlanData,
        result: InspectionValidationResult
    ):
        """Check surface finish and coating inspection requirements."""
        result.total_checks += 1

        if data.coating_requirements:
            result.passed += 1

            # Check for DFT specification
            if "dft" not in data.coating_requirements and "dry_film_thickness" not in data.coating_requirements:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="coating_dft",
                    message="Coating specified but no DFT requirement",
                    suggestion="Specify dry film thickness per SSPC/NACE standards",
                    standard_reference="SSPC-PA 2",
                ))
                result.warnings += 1

            # Add to inspection plan
            result.inspection_plan.append("Coating inspection per SSPC-PA 2")
        else:
            result.passed += 1

    def _check_pressure_test(
        self,
        data: InspectionPlanData,
        result: InspectionValidationResult
    ):
        """Check pressure test requirements."""
        result.total_checks += 1

        if data.pressure_test_required:
            if data.test_pressure_psig:
                result.passed += 1
                result.inspection_plan.append(
                    f"Hydrostatic test: {data.test_pressure_psig} psig × 30 min hold"
                )
                result.required_documentation.append("Hydrostatic Test Report")
            else:
                result.failed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="test_pressure_missing",
                    message="Pressure test required but test pressure not specified",
                    suggestion="Specify test pressure (typically 1.5× MAWP per ASME VIII)",
                    standard_reference="ASME VIII UG-99",
                ))
        else:
            result.passed += 1

    def _check_mtr_requirements(
        self,
        data: InspectionPlanData,
        result: InspectionValidationResult
    ):
        """Check MTR (Mill Test Report) requirements."""
        result.total_checks += 1

        if data.mtr_required:
            result.passed += 1
            result.required_documentation.append("MTR (Mill Test Reports)")
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="mtr_required",
                message="MTR required for material traceability",
                suggestion="Collect MTR for all pressure-retaining and structural materials",
            ))
        else:
            # Check if any codes require MTR
            mtr_required_codes = ["ASME_VIII", "ASME_B31.3", "API_661"]
            if any(code in data.applicable_codes for code in mtr_required_codes):
                result.warnings += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="mtr_not_specified",
                    message="MTR not required but code typically requires material certification",
                    suggestion="Verify MTR requirements per applicable code",
                ))
            else:
                result.passed += 1

    def _check_pwht_requirements(
        self,
        data: InspectionPlanData,
        result: InspectionValidationResult
    ):
        """Check PWHT (Post-Weld Heat Treatment) requirements."""
        result.total_checks += 1

        if data.pwht_required:
            result.passed += 1
            result.required_documentation.append("PWHT Time-Temperature Charts")
            result.inspection_plan.extend([
                "PWHT per WPS requirements",
                "Record thermocouple locations",
                "Verify heating/cooling rates",
            ])

            # Check for thick welds that typically require PWHT
            thick_welds = [w for w in data.welds if w.thickness_in > 1.5]
            if thick_welds:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="pwht_thick_welds",
                    message=f"{len(thick_welds)} welds over 1.5\" thickness - PWHT specified",
                    suggestion="Ensure proper thermocouple placement for thick sections",
                ))
        else:
            # Check if PWHT might be required
            thick_welds = [w for w in data.welds if w.thickness_in > 1.5]
            if thick_welds:
                result.warnings += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="pwht_may_be_required",
                    message=f"{len(thick_welds)} welds exceed 1.5\" - verify PWHT requirement",
                    suggestion="Check ASME VIII UCS-56 / AWS D1.1 for PWHT requirements",
                    standard_reference="ASME VIII UCS-56",
                ))
            else:
                result.passed += 1

    def _check_witness_points(
        self,
        data: InspectionPlanData,
        result: InspectionValidationResult
    ):
        """Check for witness/hold points in inspection plan."""
        result.total_checks += 1

        # Determine recommended witness points based on codes
        witness_points = []

        if "ASME_VIII" in data.applicable_codes:
            witness_points.extend([
                "Material receiving inspection (HOLD)",
                "Fit-up inspection before welding (WITNESS)",
                "Hydrostatic test (HOLD)",
                "Final inspection (HOLD)",
            ])

        if data.pwht_required:
            witness_points.append("PWHT (WITNESS)")

        if data.pressure_test_required:
            witness_points.append("Pressure test (HOLD)")

        if witness_points:
            result.passed += 1
            result.inspection_plan.extend(witness_points)
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="witness_points",
                message=f"{len(witness_points)} witness/hold points identified",
                suggestion="Coordinate with customer/AI for witness point scheduling",
            ))
        else:
            result.passed += 1

    def _generate_inspection_checklist(
        self,
        data: InspectionPlanData,
        result: InspectionValidationResult
    ):
        """Generate final inspection checklist."""
        result.total_checks += 1

        checklist = [
            f"Part: {data.part_number}",
            "=" * 40,
            "PRE-FABRICATION:",
            "  [ ] Material receiving inspection",
            "  [ ] MTR review and filing",
            "  [ ] WPS/PQR verification",
            "",
            "DURING FABRICATION:",
            "  [ ] Fit-up inspection",
            "  [ ] In-process dimensional checks",
        ]

        # Add NDE items
        if data.welds:
            checklist.append("")
            checklist.append("NDE INSPECTION:")
            all_nde = set()
            for weld in data.welds:
                all_nde.update(weld.specified_nde)
            for method in sorted(all_nde, key=lambda x: x.value):
                checklist.append(f"  [ ] {method.value} inspection")

        # Add pressure test
        if data.pressure_test_required:
            checklist.append("")
            checklist.append("PRESSURE TEST:")
            checklist.append(f"  [ ] Hydrostatic test @ {data.test_pressure_psig or '___'} psig")

        # Add final inspection items
        checklist.extend([
            "",
            "FINAL INSPECTION:",
            "  [ ] Visual inspection - all welds",
            "  [ ] Dimensional verification",
            "  [ ] Surface preparation (if coating)",
            "  [ ] Coating inspection (if applicable)",
            "  [ ] Nameplate/marking verification",
            "  [ ] Documentation package complete",
        ])

        result.inspection_plan = checklist
        result.passed += 1

    def to_dict(self, result: InspectionValidationResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "inspection_qc",
            "total_checks": result.total_checks,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "critical_failures": result.critical_failures,
            "statistics": {
                "welds_checked": result.welds_checked,
                "nde_requirements_missing": result.nde_requirements_missing,
                "documentation_gaps": result.documentation_gaps,
                "inspection_points": result.inspection_points,
            },
            "inspection_plan": result.inspection_plan,
            "required_documentation": result.required_documentation,
            "issues": [
                {
                    "severity": issue.severity.value,
                    "check_type": issue.check_type,
                    "message": issue.message,
                    "location": issue.location,
                    "suggestion": issue.suggestion,
                    "standard_reference": issue.standard_reference,
                }
                for issue in result.issues
            ],
        }
