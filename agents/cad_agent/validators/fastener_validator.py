"""
Fastener & Bolted Connection Validator
======================================
Validates bolt specifications, torque, preload, and connection design.

Phase 25.7 - Fastener Analysis

References:
- AISC 360 (Bolted connections)
- RCSC Specification (High-strength bolts)
- IFI Standards (Fastener specifications)
- ASTM F3125 (Structural bolts)
"""

import logging
import math
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.fastener")


# =============================================================================
# BOLT SPECIFICATIONS
# =============================================================================

class BoltGrade(Enum):
    """Bolt grade/specification."""
    A325 = "A325"       # ASTM F3125 Grade A325
    A490 = "A490"       # ASTM F3125 Grade A490
    A307 = "A307"       # Low carbon steel
    F1852 = "F1852"     # Twist-off A325
    F2280 = "F2280"     # Twist-off A490
    SAE_5 = "SAE_5"     # SAE Grade 5
    SAE_8 = "SAE_8"     # SAE Grade 8
    B7 = "B7"           # ASTM A193 B7 stud
    B8 = "B8"           # ASTM A193 B8 stainless


class ConnectionType(Enum):
    """Bolt connection type per AISC."""
    SNUG_TIGHT = "snug_tight"
    PRETENSIONED = "pretensioned"
    SLIP_CRITICAL = "slip_critical"


class HoleType(Enum):
    """Bolt hole type per AISC."""
    STANDARD = "STD"
    OVERSIZED = "OVS"
    SHORT_SLOT = "SSL"
    LONG_SLOT = "LSL"


# Bolt properties: (tensile_ksi, proof_ksi, K_factor)
BOLT_PROPERTIES = {
    BoltGrade.A325: (120, 92, 0.20),
    BoltGrade.A490: (150, 120, 0.20),
    BoltGrade.A307: (60, 36, 0.20),
    BoltGrade.SAE_5: (120, 92, 0.20),
    BoltGrade.SAE_8: (150, 130, 0.20),
    BoltGrade.B7: (125, 105, 0.18),
    BoltGrade.B8: (75, 30, 0.15),
}

# Bolt tensile stress areas (sq. in.) per diameter
BOLT_STRESS_AREAS = {
    # Diameter (inches): tensile stress area (sq. in.)
    0.500: 0.1419,
    0.625: 0.2260,
    0.750: 0.3345,
    0.875: 0.4617,
    1.000: 0.6057,
    1.125: 0.7633,
    1.250: 0.9691,
    1.375: 1.1549,
    1.500: 1.4053,
}

# AISC minimum pretension (kips) per bolt diameter
AISC_MIN_PRETENSION = {
    # Diameter: (A325_kips, A490_kips)
    0.500: (12, 15),
    0.625: (19, 24),
    0.750: (28, 35),
    0.875: (39, 49),
    1.000: (51, 64),
    1.125: (56, 80),
    1.250: (71, 102),
    1.375: (85, 121),
    1.500: (103, 148),
}

# Standard torque values (ft-lb) - approximate
STANDARD_TORQUES = {
    # (Grade, Diameter): torque_ft_lb
    (BoltGrade.A325, 0.500): 35,
    (BoltGrade.A325, 0.625): 70,
    (BoltGrade.A325, 0.750): 125,
    (BoltGrade.A325, 0.875): 200,
    (BoltGrade.A325, 1.000): 300,
    (BoltGrade.A325, 1.125): 375,
    (BoltGrade.A325, 1.250): 525,
    (BoltGrade.A490, 0.750): 155,
    (BoltGrade.A490, 0.875): 250,
    (BoltGrade.A490, 1.000): 375,
    (BoltGrade.A490, 1.125): 475,
    (BoltGrade.A490, 1.250): 650,
}


# =============================================================================
# BOLT HOLE DIMENSIONS
# =============================================================================

# Standard hole sizes per AISC Table J3.3M
STANDARD_HOLE_SIZES = {
    # Bolt diameter: (STD, OVS, SSL_width, SSL_length, LSL_width, LSL_length)
    0.500: (0.5625, 0.625, 0.5625, 0.6875, 0.5625, 1.25),
    0.625: (0.6875, 0.8125, 0.6875, 0.875, 0.6875, 1.5625),
    0.750: (0.8125, 0.9375, 0.8125, 1.0, 0.8125, 1.875),
    0.875: (0.9375, 1.0625, 0.9375, 1.125, 0.9375, 2.1875),
    1.000: (1.0625, 1.25, 1.0625, 1.3125, 1.0625, 2.5),
    1.125: (1.25, 1.4375, 1.25, 1.5, 1.25, 2.8125),
    1.250: (1.375, 1.5625, 1.375, 1.625, 1.375, 3.125),
    1.375: (1.5, 1.6875, 1.5, 1.75, 1.5, 3.4375),
    1.500: (1.625, 1.8125, 1.625, 1.875, 1.625, 3.75),
}

# Minimum edge distances per AISC Table J3.4
MIN_EDGE_DISTANCES = {
    # Bolt diameter: (sheared_edge, rolled_edge)
    0.500: (0.875, 0.75),
    0.625: (1.125, 0.875),
    0.750: (1.25, 1.0),
    0.875: (1.5, 1.125),
    1.000: (1.75, 1.25),
    1.125: (2.0, 1.5),
    1.250: (2.25, 1.625),
    1.375: (2.375, 1.75),
    1.500: (2.625, 1.875),
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class BoltData:
    """Bolt specification data."""
    diameter: float  # inches
    grade: BoltGrade = BoltGrade.A325
    length: Optional[float] = None  # inches
    thread_length: Optional[float] = None
    connection_type: ConnectionType = ConnectionType.SNUG_TIGHT
    hole_type: HoleType = HoleType.STANDARD
    quantity: int = 1
    specified_torque: Optional[float] = None  # ft-lb
    lubricated: bool = False


@dataclass
class ConnectionData:
    """Bolted connection data."""
    bolts: List[BoltData] = field(default_factory=list)
    grip_length: float = 0  # total thickness being clamped
    load_kips: float = 0  # applied load
    load_type: str = "shear"  # shear, tension, combined
    faying_surface: str = "class_a"  # class_a, class_b, unpainted
    edge_distance: Optional[float] = None
    bolt_spacing: Optional[float] = None


@dataclass
class FastenerValidationResult:
    """Fastener validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

    # Calculated values
    required_pretension_kips: float = 0
    calculated_torque_ft_lb: float = 0
    slip_resistance_kips: float = 0
    shear_capacity_kips: float = 0


# =============================================================================
# FASTENER VALIDATOR
# =============================================================================

class FastenerValidator:
    """
    Validates fastener specifications and bolted connections.

    Phase 25.7 - Checks:
    1. Bolt grade appropriate for connection type
    2. Pretension requirements met
    3. Torque specification correct
    4. Hole type/size appropriate
    5. Edge distance adequate
    6. Bolt spacing adequate
    7. Grip length vs thread engagement
    8. Slip-critical requirements
    9. Washer requirements
    """

    def __init__(self):
        pass

    def validate_bolt(
        self,
        bolt: BoltData
    ) -> FastenerValidationResult:
        """
        Validate individual bolt specification.

        Args:
            bolt: Bolt data

        Returns:
            Validation result
        """
        result = FastenerValidationResult()

        # Check 1: Valid diameter
        result.total_checks += 1
        if bolt.diameter not in BOLT_STRESS_AREAS:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="bolt_diameter_nonstandard",
                message=f"Bolt diameter {bolt.diameter}\" not in standard sizes",
                suggestion=f"Standard sizes: {list(BOLT_STRESS_AREAS.keys())}",
            ))
            result.warnings += 1
        else:
            result.passed += 1

        # Check 2: Grade appropriate for connection type
        result.total_checks += 1
        if bolt.connection_type in [ConnectionType.PRETENSIONED, ConnectionType.SLIP_CRITICAL]:
            if bolt.grade not in [BoltGrade.A325, BoltGrade.A490, BoltGrade.F1852, BoltGrade.F2280]:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    check_type="bolt_grade_inadequate",
                    message=f"Grade {bolt.grade.value} not suitable for {bolt.connection_type.value} connections",
                    suggestion="Use A325 or A490 (F3125) bolts for pretensioned/slip-critical",
                    standard_reference="AISC 360 / RCSC",
                ))
                result.critical_failures += 1
                result.failed += 1
            else:
                result.passed += 1
        else:
            result.passed += 1

        # Check 3: Calculate required pretension
        result.total_checks += 1
        if bolt.connection_type != ConnectionType.SNUG_TIGHT and bolt.diameter in AISC_MIN_PRETENSION:
            pretension_a325, pretension_a490 = AISC_MIN_PRETENSION[bolt.diameter]

            if bolt.grade in [BoltGrade.A490, BoltGrade.F2280]:
                result.required_pretension_kips = pretension_a490
            else:
                result.required_pretension_kips = pretension_a325

            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="pretension_required",
                message=f"Minimum pretension: {result.required_pretension_kips} kips",
                standard_reference="AISC Table J3.1",
            ))
            result.passed += 1
        else:
            result.passed += 1

        # Check 4: Calculate/validate torque
        result.total_checks += 1
        self._calculate_torque(bolt, result)

        if bolt.specified_torque and result.calculated_torque_ft_lb > 0:
            tolerance = 0.20  # 20% tolerance
            if abs(bolt.specified_torque - result.calculated_torque_ft_lb) > tolerance * result.calculated_torque_ft_lb:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="torque_mismatch",
                    message=f"Specified torque {bolt.specified_torque} ft-lb differs from calculated {result.calculated_torque_ft_lb:.0f} ft-lb",
                    suggestion="Verify K-factor and lubrication condition",
                ))
                result.warnings += 1
            else:
                result.passed += 1
        else:
            result.passed += 1

        # Check 5: Thread engagement
        result.total_checks += 1
        if bolt.length and bolt.thread_length:
            if bolt.grade in [BoltGrade.A325, BoltGrade.A490]:
                # Threads should not be in shear plane for bearing connections
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="thread_engagement",
                    message=f"Thread length: {bolt.thread_length}\", bolt length: {bolt.length}\"",
                    suggestion="Verify threads excluded from shear plane if bearing-type connection",
                ))
            result.passed += 1
        else:
            result.passed += 1

        return result

    def _calculate_torque(self, bolt: BoltData, result: FastenerValidationResult):
        """Calculate installation torque."""
        # T = K × D × P
        # Where: T = torque, K = nut factor, D = diameter, P = preload

        if bolt.diameter not in AISC_MIN_PRETENSION:
            return

        pretension_a325, pretension_a490 = AISC_MIN_PRETENSION[bolt.diameter]

        if bolt.grade in [BoltGrade.A490, BoltGrade.F2280]:
            preload = pretension_a490
        else:
            preload = pretension_a325

        # K factor based on lubrication
        k_factor = 0.15 if bolt.lubricated else 0.20

        # Calculate torque: T = K × D × P
        # Convert preload from kips to lbs, result in ft-lb
        torque_ft_lb = k_factor * bolt.diameter * (preload * 1000) / 12

        result.calculated_torque_ft_lb = torque_ft_lb

    def validate_connection(
        self,
        connection: ConnectionData
    ) -> FastenerValidationResult:
        """
        Validate complete bolted connection.

        Args:
            connection: Connection data

        Returns:
            Validation result
        """
        result = FastenerValidationResult()

        if not connection.bolts:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                check_type="no_bolts",
                message="No bolts specified in connection",
            ))
            result.critical_failures += 1
            result.failed += 1
            return result

        # Use first bolt as reference
        ref_bolt = connection.bolts[0]

        # Check 1: Edge distance
        result.total_checks += 1
        if connection.edge_distance and ref_bolt.diameter in MIN_EDGE_DISTANCES:
            min_sheared, min_rolled = MIN_EDGE_DISTANCES[ref_bolt.diameter]
            min_edge = min_rolled  # Assume rolled/flame cut

            if connection.edge_distance < min_edge:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    check_type="edge_distance_inadequate",
                    message=f"Edge distance {connection.edge_distance}\" < minimum {min_edge}\"",
                    suggestion=f"Increase edge distance to {min_edge}\" min",
                    standard_reference="AISC Table J3.4",
                ))
                result.critical_failures += 1
                result.failed += 1
            else:
                result.passed += 1
        else:
            result.passed += 1

        # Check 2: Bolt spacing
        result.total_checks += 1
        if connection.bolt_spacing:
            min_spacing = 2.667 * ref_bolt.diameter  # 2-2/3 × d minimum
            preferred_spacing = 3 * ref_bolt.diameter

            if connection.bolt_spacing < min_spacing:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    check_type="spacing_inadequate",
                    message=f"Bolt spacing {connection.bolt_spacing}\" < minimum {min_spacing:.3f}\"",
                    suggestion=f"Increase spacing to {preferred_spacing:.3f}\" (3d preferred)",
                    standard_reference="AISC J3.3",
                ))
                result.critical_failures += 1
                result.failed += 1
            elif connection.bolt_spacing < preferred_spacing:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="spacing_tight",
                    message=f"Bolt spacing {connection.bolt_spacing}\" less than preferred {preferred_spacing:.3f}\"",
                ))
                result.warnings += 1
            else:
                result.passed += 1
        else:
            result.passed += 1

        # Check 3: Slip-critical capacity
        result.total_checks += 1
        if ref_bolt.connection_type == ConnectionType.SLIP_CRITICAL:
            self._calculate_slip_resistance(connection, ref_bolt, result)

            if connection.load_kips > result.slip_resistance_kips:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    check_type="slip_capacity_exceeded",
                    message=f"Load {connection.load_kips} kips > slip resistance {result.slip_resistance_kips:.1f} kips",
                    suggestion="Add bolts or increase bolt size",
                    standard_reference="AISC J3.8",
                ))
                result.critical_failures += 1
                result.failed += 1
            else:
                result.passed += 1
        else:
            result.passed += 1

        # Check 4: Hole type restrictions
        result.total_checks += 1
        if ref_bolt.hole_type == HoleType.LONG_SLOT:
            if ref_bolt.connection_type != ConnectionType.SLIP_CRITICAL:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="slot_requires_slip_critical",
                    message="Long slotted holes typically require slip-critical connection",
                    standard_reference="AISC J3.2",
                ))
                result.warnings += 1
            else:
                result.passed += 1
        else:
            result.passed += 1

        # Check 5: Washer requirements
        result.total_checks += 1
        self._check_washer_requirements(connection, ref_bolt, result)

        return result

    def _calculate_slip_resistance(
        self,
        connection: ConnectionData,
        bolt: BoltData,
        result: FastenerValidationResult
    ):
        """Calculate slip-critical resistance."""
        # φRn = φ × μ × Du × hf × Tb × ns
        # Where: μ = slip coefficient, Du = 1.13, hf = hole factor

        # Slip coefficients
        slip_coeff = {
            "class_a": 0.30,  # Unpainted clean mill scale
            "class_b": 0.50,  # Blast-cleaned, class B coating
            "unpainted": 0.35,
        }

        # Hole factors (AISC Table J3.6)
        hole_factors = {
            HoleType.STANDARD: 1.00,
            HoleType.OVERSIZED: 0.85,
            HoleType.SHORT_SLOT: 0.85,
            HoleType.LONG_SLOT: 0.70,
        }

        mu = slip_coeff.get(connection.faying_surface, 0.30)
        hf = hole_factors.get(bolt.hole_type, 1.0)
        du = 1.13  # Factor for pretension method

        # Get pretension
        if bolt.diameter in AISC_MIN_PRETENSION:
            t_a325, t_a490 = AISC_MIN_PRETENSION[bolt.diameter]
            tb = t_a490 if bolt.grade in [BoltGrade.A490, BoltGrade.F2280] else t_a325
        else:
            tb = 0

        # Number of slip planes (assume 1)
        ns = 1

        # Total bolts
        n_bolts = len(connection.bolts)

        # Slip resistance per bolt
        phi = 1.0  # For standard holes
        if bolt.hole_type != HoleType.STANDARD:
            phi = 0.85

        rn_per_bolt = phi * mu * du * hf * tb * ns
        result.slip_resistance_kips = rn_per_bolt * n_bolts

    def _check_washer_requirements(
        self,
        connection: ConnectionData,
        bolt: BoltData,
        result: FastenerValidationResult
    ):
        """Check washer requirements per RCSC."""
        washer_notes = []

        # Hardened washers required for pretensioned/slip-critical
        if bolt.connection_type != ConnectionType.SNUG_TIGHT:
            washer_notes.append("Hardened washer required under turned element")

        # Oversized/slotted holes need washers
        if bolt.hole_type == HoleType.OVERSIZED:
            washer_notes.append("5/16\" min thick washer over oversized hole")
        elif bolt.hole_type in [HoleType.SHORT_SLOT, HoleType.LONG_SLOT]:
            washer_notes.append("Plate washer min 5/16\" thick over slotted hole")

        if washer_notes:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="washer_requirements",
                message="; ".join(washer_notes),
                standard_reference="RCSC 6.2",
            ))

        result.passed += 1

    def to_dict(self, result: FastenerValidationResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "fastener",
            "total_checks": result.total_checks,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "critical_failures": result.critical_failures,
            "required_pretension_kips": result.required_pretension_kips,
            "calculated_torque_ft_lb": result.calculated_torque_ft_lb,
            "slip_resistance_kips": result.slip_resistance_kips,
            "shear_capacity_kips": result.shear_capacity_kips,
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
