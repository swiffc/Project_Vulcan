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


# =============================================================================
# PHASE 25.5 - MACHINING TOLERANCE VALIDATION
# =============================================================================

# Achievable tolerances by machining process (inches)
PROCESS_TOLERANCES = {
    # Process: (typical_tolerance, best_tolerance, surface_finish_ra)
    "rough_turning": (0.010, 0.005, 250),
    "finish_turning": (0.002, 0.001, 63),
    "precision_turning": (0.0005, 0.0002, 32),
    "rough_milling": (0.010, 0.005, 250),
    "finish_milling": (0.002, 0.001, 63),
    "precision_milling": (0.0005, 0.0002, 32),
    "drilling": (0.005, 0.002, 125),
    "reaming": (0.001, 0.0005, 63),
    "boring": (0.001, 0.0003, 32),
    "grinding_cylindrical": (0.0005, 0.0001, 16),
    "grinding_surface": (0.0005, 0.0001, 16),
    "honing": (0.0002, 0.00005, 8),
    "lapping": (0.0001, 0.00002, 4),
    "broaching": (0.001, 0.0005, 63),
    "edm_wire": (0.0005, 0.0001, 32),
    "edm_sinker": (0.001, 0.0002, 63),
}

# Standard fit classes per ANSI B4.1 (hole basis)
FIT_CLASSES = {
    # Class: (hole_tolerance_grade, shaft_tolerance_grade, clearance_type)
    "RC1": ("H5", "g4", "close_running"),
    "RC2": ("H6", "g5", "free_running"),
    "RC3": ("H7", "f6", "medium_running"),
    "RC4": ("H8", "f7", "close_sliding"),
    "RC5": ("H8", "e7", "locational_clearance"),
    "RC6": ("H9", "e8", "locational_clearance"),
    "RC7": ("H10", "d9", "loose_running"),
    "LC1": ("H6", "h5", "locational_clearance"),
    "LC2": ("H7", "h6", "locational_clearance"),
    "LC3": ("H8", "h7", "locational_clearance"),
    "LT1": ("H7", "js6", "locational_transition"),
    "LT2": ("H8", "js7", "locational_transition"),
    "LN1": ("H6", "n5", "locational_interference"),
    "LN2": ("H7", "p6", "locational_interference"),
    "LN3": ("H7", "r6", "locational_interference"),
    "FN1": ("H6", "n5", "light_drive"),
    "FN2": ("H7", "p6", "medium_drive"),
    "FN3": ("H7", "r6", "heavy_drive"),
    "FN4": ("H7", "s6", "force_fit"),
    "FN5": ("H8", "u7", "shrink_fit"),
}

# ISO tolerance grades (IT grades) - tolerance values at 25mm nominal
ISO_TOLERANCE_GRADES = {
    # IT Grade: tolerance in mm at 25mm nominal
    "IT01": 0.0003,
    "IT0": 0.0005,
    "IT1": 0.0008,
    "IT2": 0.0012,
    "IT3": 0.002,
    "IT4": 0.003,
    "IT5": 0.005,
    "IT6": 0.008,
    "IT7": 0.013,
    "IT8": 0.021,
    "IT9": 0.033,
    "IT10": 0.052,
    "IT11": 0.084,
    "IT12": 0.130,
    "IT13": 0.210,
    "IT14": 0.330,
    "IT15": 0.520,
    "IT16": 0.840,
}


@dataclass
class MachiningToleranceData:
    """Data for machining tolerance validation."""
    feature_type: str  # shaft, bore, face, slot, keyway
    nominal_size: float  # inches
    tolerance_plus: float  # inches
    tolerance_minus: float  # inches
    surface_finish_ra: Optional[int] = None  # microinches
    fit_class: Optional[str] = None  # RC1, LC2, FN3, etc.
    process_specified: Optional[str] = None


@dataclass
class MachiningToleranceResult:
    """Result of machining tolerance validation."""
    achievable: bool = True
    recommended_process: Optional[str] = None
    estimated_cost_factor: float = 1.0  # 1.0 = standard, higher = more expensive
    issues: List[ValidationIssue] = field(default_factory=list)
    total_checks: int = 0
    passed: int = 0
    warnings: int = 0


class MachiningToleranceValidator:
    """
    Validates machining tolerances are achievable and cost-effective.

    Phase 25.5 - Checks:
    1. Tolerance achievable with specified/standard processes
    2. Surface finish achievable
    3. Fit class requirements met
    4. Cost-effective process selection
    5. Geometric tolerance achievability
    """

    def __init__(self):
        pass

    def validate_tolerance(
        self,
        data: MachiningToleranceData
    ) -> MachiningToleranceResult:
        """
        Validate if specified tolerance is achievable.

        Args:
            data: Machining tolerance data

        Returns:
            Validation result with recommended process
        """
        result = MachiningToleranceResult()
        total_tolerance = abs(data.tolerance_plus) + abs(data.tolerance_minus)

        # Check 1: Find suitable process
        result.total_checks += 1
        suitable_processes = []

        for process, (typical, best, finish) in PROCESS_TOLERANCES.items():
            if best <= total_tolerance:
                suitable_processes.append((process, typical, best))

        if not suitable_processes:
            result.achievable = False
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                check_type="tolerance_unachievable",
                message=f"Tolerance ±{total_tolerance/2:.5f}\" may not be achievable with standard machining",
                suggestion="Consider: (1) Lapping/honing, (2) Relaxing tolerance, (3) Special process",
            ))
        else:
            # Sort by cost (simpler processes first)
            process_cost = {
                "rough_turning": 1, "rough_milling": 1, "drilling": 1,
                "finish_turning": 2, "finish_milling": 2, "reaming": 2, "broaching": 2,
                "precision_turning": 3, "precision_milling": 3, "boring": 3,
                "grinding_cylindrical": 4, "grinding_surface": 4, "edm_wire": 4, "edm_sinker": 4,
                "honing": 5, "lapping": 6,
            }
            suitable_processes.sort(key=lambda x: process_cost.get(x[0], 10))

            result.recommended_process = suitable_processes[0][0]
            result.estimated_cost_factor = process_cost.get(result.recommended_process, 1)
            result.passed += 1

            if result.estimated_cost_factor >= 4:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="tolerance_expensive",
                    message=f"Tolerance requires {result.recommended_process} (cost factor: {result.estimated_cost_factor}x)",
                    suggestion="Consider if tolerance can be relaxed",
                ))
                result.warnings += 1

        # Check 2: Surface finish achievability
        result.total_checks += 1
        if data.surface_finish_ra:
            achievable_finishes = [
                (p, f) for p, (_, _, f) in PROCESS_TOLERANCES.items()
                if f <= data.surface_finish_ra
            ]

            if not achievable_finishes:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="finish_difficult",
                    message=f"Surface finish Ra {data.surface_finish_ra} μin requires special processing",
                    suggestion="Consider honing or lapping for ultra-fine finishes",
                ))
                result.warnings += 1
            else:
                result.passed += 1
        else:
            result.passed += 1

        # Check 3: Fit class validation
        result.total_checks += 1
        if data.fit_class and data.fit_class in FIT_CLASSES:
            hole_grade, shaft_grade, fit_type = FIT_CLASSES[data.fit_class]
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="fit_class_info",
                message=f"Fit class {data.fit_class}: {fit_type} (Hole: {hole_grade}, Shaft: {shaft_grade})",
                standard_reference="ANSI B4.1",
            ))
            result.passed += 1
        else:
            result.passed += 1

        # Check 4: Tolerance symmetry
        result.total_checks += 1
        if data.tolerance_plus != 0 and data.tolerance_minus != 0:
            ratio = abs(data.tolerance_plus / data.tolerance_minus) if data.tolerance_minus != 0 else 999
            if ratio > 4 or ratio < 0.25:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="asymmetric_tolerance",
                    message=f"Asymmetric tolerance +{data.tolerance_plus}/-{data.tolerance_minus}\"",
                    suggestion="Verify asymmetric tolerance is intentional for fit requirements",
                ))
            result.passed += 1
        else:
            result.passed += 1

        return result

    def check_geometric_tolerance(
        self,
        tolerance_type: str,  # flatness, parallelism, perpendicularity, runout, concentricity
        tolerance_value: float,  # inches
        feature_size: float,  # inches (length or diameter)
    ) -> MachiningToleranceResult:
        """
        Check if geometric tolerance is achievable.

        Args:
            tolerance_type: Type of geometric tolerance
            tolerance_value: Specified tolerance value
            feature_size: Size of the feature being toleranced

        Returns:
            Validation result
        """
        result = MachiningToleranceResult()

        # Typical achievable geometric tolerances (inches per inch of length)
        geo_tolerance_limits = {
            "flatness": 0.0001,  # per inch of span
            "parallelism": 0.0002,  # per inch of length
            "perpendicularity": 0.0002,  # per inch of height
            "runout": 0.0005,  # TIR on diameter
            "concentricity": 0.001,  # TIR
            "cylindricity": 0.0005,  # per inch of length
            "circularity": 0.0003,  # on diameter
            "position": 0.001,  # typical position tolerance
        }

        result.total_checks += 1

        limit_per_unit = geo_tolerance_limits.get(tolerance_type.lower(), 0.001)

        # Scale limit by feature size
        if tolerance_type.lower() in ["flatness", "parallelism", "perpendicularity", "cylindricity"]:
            achievable_limit = limit_per_unit * feature_size
        else:
            achievable_limit = limit_per_unit

        if tolerance_value < achievable_limit:
            result.achievable = False
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="geometric_tolerance_tight",
                message=f"{tolerance_type.title()} tolerance {tolerance_value:.5f}\" very tight for {feature_size}\" feature",
                suggestion=f"Typical achievable: {achievable_limit:.5f}\" - may require grinding/lapping",
            ))
            result.warnings += 1
        else:
            result.passed += 1

        return result

    def to_dict(self, result: MachiningToleranceResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "machining_tolerance",
            "achievable": result.achievable,
            "recommended_process": result.recommended_process,
            "estimated_cost_factor": result.estimated_cost_factor,
            "total_checks": result.total_checks,
            "passed": result.passed,
            "warnings": result.warnings,
            "issues": [
                {
                    "severity": issue.severity.value,
                    "check_type": issue.check_type,
                    "message": issue.message,
                    "suggestion": issue.suggestion,
                    "standard_reference": issue.standard_reference,
                }
                for issue in result.issues
            ],
        }
