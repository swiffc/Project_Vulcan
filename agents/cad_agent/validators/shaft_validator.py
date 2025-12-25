"""
Shaft & Machining Validator
===========================
Validates machined components (shafts, bores, keyways).

Phase 25.5 - Machining Analysis
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.shaft")


# Standard keyway widths per ANSI B17.1
STANDARD_KEYWAY_WIDTHS = {
    # shaft_dia_range: (key_width, key_depth)
    (0.3125, 0.4375): (0.09375, 0.09375),   # 5/16" - 7/16"
    (0.5, 0.5625): (0.125, 0.0625),          # 1/2" - 9/16"
    (0.625, 0.875): (0.1875, 0.09375),       # 5/8" - 7/8"
    (0.9375, 1.25): (0.25, 0.125),           # 15/16" - 1-1/4"
    (1.3125, 1.375): (0.3125, 0.15625),      # 1-5/16" - 1-3/8"
    (1.4375, 1.75): (0.375, 0.1875),         # 1-7/16" - 1-3/4"
    (1.8125, 2.25): (0.5, 0.25),             # 1-13/16" - 2-1/4"
    (2.3125, 2.75): (0.625, 0.3125),         # 2-5/16" - 2-3/4"
    (2.8125, 3.25): (0.75, 0.375),           # 2-13/16" - 3-1/4"
    (3.3125, 3.75): (0.875, 0.4375),         # 3-5/16" - 3-3/4"
    (3.8125, 4.5): (1.0, 0.5),               # 3-13/16" - 4-1/2"
}

# Standard surface finishes (Ra in microinches)
SURFACE_FINISH_REQUIREMENTS = {
    "bearing_journal": 16,      # Bearing seats
    "seal_surface": 16,         # Shaft seal areas
    "keyway": 63,               # Keyway surfaces
    "general_machined": 125,    # General machined surfaces
    "ground": 16,               # Ground surfaces
    "as_turned": 125,           # As-turned surfaces
}

# Standard retaining ring groove widths (Truarc/Rotor Clip)
RETAINING_RING_GROOVES = {
    # shaft_dia: (groove_width, groove_depth)
    0.75: (0.035, 0.031),
    0.875: (0.042, 0.037),
    1.0: (0.046, 0.039),
    1.125: (0.046, 0.043),
    1.25: (0.05, 0.047),
    1.375: (0.05, 0.051),
    1.5: (0.062, 0.055),
    1.75: (0.062, 0.063),
    2.0: (0.078, 0.071),
    2.25: (0.078, 0.079),
    2.5: (0.093, 0.087),
    2.75: (0.093, 0.095),
    3.0: (0.109, 0.103),
}


@dataclass
class ShaftData:
    """Data for a shaft or machined feature."""
    diameter: float  # inches
    length: Optional[float] = None
    tolerance_plus: Optional[float] = None
    tolerance_minus: Optional[float] = None
    surface_finish_ra: Optional[int] = None  # microinches
    runout_tir: Optional[float] = None
    concentricity: Optional[float] = None


@dataclass
class KeywayData:
    """Data for a keyway."""
    width: float
    depth: float
    length: Optional[float] = None
    angular_location: Optional[float] = None  # degrees from reference


@dataclass
class ShaftValidationResult:
    """Shaft validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

    # Statistics
    missing_callouts: List[str] = field(default_factory=list)


class ShaftValidator:
    """
    Validates shaft and machining requirements.

    Checks:
    1. Diameter tolerances achievable
    2. Length tolerances specified
    3. Keyway dimensions per ANSI B17.1
    4. Keyway angular location specified
    5. Surface finish Ra specified
    6. Runout/TIR specification
    7. Concentricity specification
    8. Retaining ring groove dimensions
    9. Chamfers on shaft ends
    10. Heat treatment requirements
    """

    def __init__(self):
        pass

    def validate_shaft(
        self,
        shaft: ShaftData,
        feature_type: str = "general"
    ) -> ShaftValidationResult:
        """
        Validate a shaft or cylindrical feature.

        Args:
            shaft: Shaft data
            feature_type: "bearing_journal", "seal_surface", "general"

        Returns:
            Validation result
        """
        result = ShaftValidationResult()

        # Check diameter tolerance
        self._check_diameter_tolerance(shaft, result)

        # Check surface finish
        self._check_surface_finish(shaft, feature_type, result)

        # Check runout for bearing journals
        if feature_type == "bearing_journal":
            self._check_runout(shaft, result)
            self._check_concentricity(shaft, result)

        return result

    def _check_diameter_tolerance(self, shaft: ShaftData, result: ShaftValidationResult):
        """Check if diameter tolerance is specified and achievable."""
        result.total_checks += 1

        if shaft.tolerance_plus is None and shaft.tolerance_minus is None:
            result.missing_callouts.append("diameter_tolerance")
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="tolerance_missing",
                message=f"Diameter {shaft.diameter}\" missing tolerance callout",
                suggestion="Add tolerance (e.g., +0.000/-0.001 for bearing fit)",
            ))
            result.warnings += 1
            return

        # Check if tolerance is achievable
        total_tol = abs(shaft.tolerance_plus or 0) + abs(shaft.tolerance_minus or 0)

        if total_tol < 0.0005:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="tolerance_tight",
                message=f"Total tolerance {total_tol:.4f}\" very tight - requires grinding",
                suggestion="Verify grinding is specified and quoted",
            ))
            result.warnings += 1
        elif total_tol < 0.002:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="tolerance_precision",
                message=f"Precision tolerance {total_tol:.4f}\" - finish turning required",
            ))
            result.passed += 1
        else:
            result.passed += 1

    def _check_surface_finish(
        self,
        shaft: ShaftData,
        feature_type: str,
        result: ShaftValidationResult
    ):
        """Check surface finish specification."""
        result.total_checks += 1

        required_finish = SURFACE_FINISH_REQUIREMENTS.get(feature_type, 125)

        if shaft.surface_finish_ra is None:
            if feature_type in ["bearing_journal", "seal_surface"]:
                result.missing_callouts.append("surface_finish")
                result.critical_failures += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    check_type="surface_finish_missing",
                    message=f"Surface finish not specified for {feature_type}",
                    suggestion=f"Add surface finish callout (Ra {required_finish} μin typical)",
                ))
                result.failed += 1
            else:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="surface_finish_not_called",
                    message="Surface finish not specified (standard shop practice applies)",
                ))
                result.passed += 1
        elif shaft.surface_finish_ra > required_finish:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="surface_finish_coarse",
                message=f"Surface finish Ra {shaft.surface_finish_ra} μin coarser than recommended {required_finish} μin for {feature_type}",
                suggestion=f"Consider Ra {required_finish} μin or finer",
            ))
            result.warnings += 1
        else:
            result.passed += 1

    def _check_runout(self, shaft: ShaftData, result: ShaftValidationResult):
        """Check runout/TIR specification for bearing journals."""
        result.total_checks += 1

        if shaft.runout_tir is None:
            result.missing_callouts.append("runout")
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="runout_missing",
                message="Runout (TIR) not specified for bearing journal",
                suggestion="Add TIR callout (typically 0.001-0.002\" for bearings)",
            ))
            result.warnings += 1
        elif shaft.runout_tir > 0.002:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="runout_loose",
                message=f"TIR {shaft.runout_tir}\" may be too loose for precision bearing",
                suggestion="Typical TIR for bearings: 0.001-0.002\"",
            ))
            result.warnings += 1
        else:
            result.passed += 1

    def _check_concentricity(self, shaft: ShaftData, result: ShaftValidationResult):
        """Check concentricity specification."""
        result.total_checks += 1

        if shaft.concentricity is None:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="concentricity_not_called",
                message="Concentricity not specified (runout may control)",
            ))
            result.passed += 1
        else:
            result.passed += 1

    def validate_keyway(
        self,
        keyway: KeywayData,
        shaft_diameter: float
    ) -> ShaftValidationResult:
        """
        Validate keyway dimensions against ANSI B17.1.

        Args:
            keyway: Keyway data
            shaft_diameter: Shaft diameter

        Returns:
            Validation result
        """
        result = ShaftValidationResult()

        # Find standard keyway size for shaft diameter
        standard_width = None
        standard_depth = None

        for (min_d, max_d), (width, depth) in STANDARD_KEYWAY_WIDTHS.items():
            if min_d <= shaft_diameter <= max_d:
                standard_width = width
                standard_depth = depth
                break

        # Check width
        result.total_checks += 1
        if standard_width:
            if abs(keyway.width - standard_width) > 0.001:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="keyway_width",
                    message=f"Keyway width {keyway.width}\" differs from ANSI standard {standard_width}\"",
                    suggestion=f"Standard keyway for {shaft_diameter}\" shaft: {standard_width}\" wide",
                    standard_reference="ANSI B17.1",
                ))
                result.warnings += 1
            else:
                result.passed += 1
        else:
            result.passed += 1

        # Check depth
        result.total_checks += 1
        if standard_depth:
            if abs(keyway.depth - standard_depth) > 0.01:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="keyway_depth",
                    message=f"Keyway depth {keyway.depth}\" differs from ANSI standard {standard_depth}\"",
                    standard_reference="ANSI B17.1",
                ))
            result.passed += 1
        else:
            result.passed += 1

        # Check angular location
        result.total_checks += 1
        if keyway.angular_location is None:
            result.missing_callouts.append("keyway_angular_location")
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                check_type="keyway_location_missing",
                message="Keyway angular location not specified",
                suggestion="Add keyway angular location reference (e.g., 0° from flat)",
            ))
            result.critical_failures += 1
            result.failed += 1
        else:
            result.passed += 1

        return result

    def validate_retaining_ring_groove(
        self,
        shaft_diameter: float,
        groove_width: Optional[float] = None,
        groove_depth: Optional[float] = None
    ) -> ShaftValidationResult:
        """
        Validate retaining ring groove dimensions.

        Args:
            shaft_diameter: Shaft diameter at groove
            groove_width: Measured/specified groove width
            groove_depth: Measured/specified groove depth

        Returns:
            Validation result
        """
        result = ShaftValidationResult()

        # Find closest standard
        closest_dia = min(RETAINING_RING_GROOVES.keys(), key=lambda x: abs(x - shaft_diameter))

        if abs(closest_dia - shaft_diameter) > 0.125:
            result.total_checks += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="retaining_ring_size",
                message=f"Shaft {shaft_diameter}\" not standard retaining ring size",
                suggestion="Verify retaining ring availability for this diameter",
            ))
            result.passed += 1
            return result

        std_width, std_depth = RETAINING_RING_GROOVES[closest_dia]

        # Check width
        result.total_checks += 1
        if groove_width is None:
            result.missing_callouts.append("ring_groove_width")
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="ring_groove_width_missing",
                message="Retaining ring groove width not specified",
                suggestion=f"Standard groove width for {closest_dia}\" shaft: {std_width}\"",
            ))
            result.warnings += 1
        elif abs(groove_width - std_width) > 0.005:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="ring_groove_width",
                message=f"Groove width {groove_width}\" differs from catalog {std_width}\"",
                suggestion="Verify ring catalog dimensions",
            ))
            result.warnings += 1
        else:
            result.passed += 1

        return result

    def check_chamfers(
        self,
        has_chamfer: bool,
        chamfer_size: Optional[float] = None
    ) -> ShaftValidationResult:
        """Check shaft end chamfers."""
        result = ShaftValidationResult()
        result.total_checks += 1

        if not has_chamfer:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="chamfer_missing",
                message="Shaft end chamfer not shown",
                suggestion="Add chamfer for assembly ease (45° x 1/32\" typical)",
            ))
            result.passed += 1
        elif chamfer_size and chamfer_size < 0.03:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="chamfer_small",
                message=f"Chamfer {chamfer_size}\" may be too small for easy assembly",
            ))
            result.passed += 1
        else:
            result.passed += 1

        return result

    def to_dict(self, result: ShaftValidationResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "shaft",
            "total_checks": result.total_checks,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "critical_failures": result.critical_failures,
            "missing_callouts": result.missing_callouts,
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
