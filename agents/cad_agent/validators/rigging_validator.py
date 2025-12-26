"""
Rigging & Lift Point Validator
==============================
Validates lifting lugs, rigging hardware, and lift point placement.

Phase 25.8 - Rigging Analysis

References:
- ASME BTH-1 (Design of Below-the-Hook Lifting Devices)
- OSHA 1926.251 (Rigging Equipment)
- AISC Design Guide 17 (High Strength Bolts)
"""

import logging
import math
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.rigging")


# =============================================================================
# LIFTING EQUIPMENT SPECIFICATIONS
# =============================================================================

class LiftingDeviceType(Enum):
    """Types of lifting devices."""
    LUG_PLATE = "lug_plate"
    TRUNNION = "trunnion"
    LIFTING_EYE = "lifting_eye"
    PAD_EYE = "pad_eye"
    SPREADER_BEAM = "spreader_beam"
    SHACKLE = "shackle"


class LoadClass(Enum):
    """ASME BTH-1 Load Classes."""
    CLASS_A = "A"  # Design factor 3.0 (normal service)
    CLASS_B = "B"  # Design factor 4.0 (heavy service)
    CLASS_C = "C"  # Design factor 5.0 (severe service)
    CLASS_D = "D"  # Design factor 6.0 (critical service)


# Design factors per ASME BTH-1
DESIGN_FACTORS = {
    LoadClass.CLASS_A: 3.0,
    LoadClass.CLASS_B: 4.0,
    LoadClass.CLASS_C: 5.0,
    LoadClass.CLASS_D: 6.0,
}

# Standard shackle capacities (tons) - Crosby type
SHACKLE_CAPACITIES = {
    # Shackle size (inches): WLL (tons)
    0.25: 0.5,
    0.375: 1.0,
    0.5: 2.0,
    0.625: 3.25,
    0.75: 4.75,
    0.875: 6.5,
    1.0: 8.5,
    1.125: 9.5,
    1.25: 12.0,
    1.375: 13.5,
    1.5: 17.0,
    1.75: 25.0,
    2.0: 35.0,
    2.5: 55.0,
    3.0: 85.0,
}

# Sling angles and capacity reduction
SLING_ANGLE_FACTORS = {
    # Angle from horizontal (degrees): capacity factor
    90: 1.000,  # Vertical
    60: 0.866,
    45: 0.707,
    30: 0.500,
}

# Wire rope sling capacities (tons) - 6x19 IWRC
WIRE_ROPE_CAPACITIES = {
    # Diameter (inches): (vertical, choker, basket_90deg)
    0.25: (0.56, 0.42, 1.12),
    0.375: (1.3, 0.97, 2.6),
    0.5: (2.3, 1.7, 4.6),
    0.625: (3.6, 2.7, 7.2),
    0.75: (5.1, 3.8, 10.2),
    0.875: (6.9, 5.2, 13.8),
    1.0: (9.0, 6.7, 18.0),
    1.125: (11.0, 8.2, 22.0),
    1.25: (14.0, 10.0, 28.0),
}


# =============================================================================
# LIFTING LUG DESIGN PARAMETERS
# =============================================================================

# Minimum dimensions for plate lifting lugs
LUG_DESIGN_MINIMUMS = {
    # (min_pin_hole_dia_ratio, min_edge_dist_ratio, min_plate_thick_ratio)
    "lug_plate": (1.0, 1.5, 0.5),  # hole_dia × factors
}

# Stress limits per ASME BTH-1 (ksi)
STRESS_LIMITS = {
    # Material: (Fy, Fu)
    "A36": (36, 58),
    "A572-50": (50, 65),
    "A514": (100, 110),
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class LiftingLugData:
    """Lifting lug geometry and specifications."""
    device_type: LiftingDeviceType = LiftingDeviceType.LUG_PLATE
    load_class: LoadClass = LoadClass.CLASS_A

    # Geometry
    plate_thickness: float = 0  # inches
    plate_width: float = 0  # inches
    hole_diameter: float = 0  # inches
    edge_distance: float = 0  # from hole center to plate edge
    throat_width: float = 0  # narrowest section width

    # Material
    material: str = "A36"

    # Load
    rated_load_lbs: float = 0
    sling_angle_deg: float = 90  # from horizontal

    # Weld
    weld_size: float = 0  # fillet weld leg size
    weld_length: float = 0  # total weld length


@dataclass
class RiggingData:
    """Complete rigging arrangement data."""
    total_load_lbs: float = 0
    center_of_gravity: Tuple[float, float, float] = (0, 0, 0)  # (x, y, z)
    lift_points: List[Tuple[float, float, float]] = field(default_factory=list)  # (x, y, z) locations
    sling_type: str = "wire_rope"  # wire_rope, chain, synthetic
    number_of_legs: int = 4


@dataclass
class RiggingValidationResult:
    """Rigging validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

    # Calculated values
    required_capacity_lbs: float = 0
    design_factor: float = 3.0
    lug_capacity_lbs: float = 0
    shear_stress_ksi: float = 0
    bearing_stress_ksi: float = 0
    tensile_stress_ksi: float = 0


# =============================================================================
# RIGGING VALIDATOR
# =============================================================================

class RiggingValidator:
    """
    Validates lifting lugs and rigging arrangements.

    Phase 25.8 - Checks:
    1. Lifting lug geometry adequacy
    2. Stress check (shear, bearing, tensile)
    3. Weld sizing
    4. Center of gravity vs lift point placement
    5. Sling angle effects
    6. Shackle/hardware capacity
    7. Design factor per ASME BTH-1
    8. Load distribution
    """

    def __init__(self):
        pass

    def validate_lifting_lug(
        self,
        lug: LiftingLugData
    ) -> RiggingValidationResult:
        """
        Validate lifting lug design per ASME BTH-1.

        Args:
            lug: Lifting lug data

        Returns:
            Validation result
        """
        result = RiggingValidationResult()
        result.design_factor = DESIGN_FACTORS.get(lug.load_class, 3.0)

        # Get material properties
        material_props = STRESS_LIMITS.get(lug.material, STRESS_LIMITS["A36"])
        fy, fu = material_props

        # Calculate required capacity with design factor
        result.required_capacity_lbs = lug.rated_load_lbs * result.design_factor

        # Account for sling angle
        if lug.sling_angle_deg < 90:
            angle_rad = math.radians(lug.sling_angle_deg)
            sling_factor = 1 / math.sin(angle_rad)
            result.required_capacity_lbs *= sling_factor

        # Check 1: Minimum edge distance
        result.total_checks += 1
        min_edge_dist = lug.hole_diameter * 1.5  # 1.5 × hole diameter minimum

        if lug.edge_distance < min_edge_dist:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                check_type="edge_distance_inadequate",
                message=f"Edge distance {lug.edge_distance}\" < minimum {min_edge_dist:.3f}\"",
                suggestion=f"Increase edge distance to {min_edge_dist:.3f}\" min (1.5 × hole dia)",
                standard_reference="ASME BTH-1",
            ))
            result.critical_failures += 1
            result.failed += 1
        else:
            result.passed += 1

        # Check 2: Shear stress at pin
        result.total_checks += 1
        shear_area = 2 * lug.plate_thickness * (lug.edge_distance - lug.hole_diameter / 2)

        if shear_area > 0:
            result.shear_stress_ksi = (result.required_capacity_lbs / 1000) / shear_area
            allowable_shear = 0.4 * fy

            if result.shear_stress_ksi > allowable_shear:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    check_type="shear_stress_exceeded",
                    message=f"Shear stress {result.shear_stress_ksi:.1f} ksi > allowable {allowable_shear:.1f} ksi",
                    suggestion="Increase plate thickness or edge distance",
                    standard_reference="ASME BTH-1 3-3.3",
                ))
                result.critical_failures += 1
                result.failed += 1
            else:
                result.passed += 1
        else:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                check_type="geometry_invalid",
                message="Invalid lug geometry - cannot calculate shear area",
            ))
            result.failed += 1

        # Check 3: Bearing stress
        result.total_checks += 1
        bearing_area = lug.hole_diameter * lug.plate_thickness

        if bearing_area > 0:
            result.bearing_stress_ksi = (result.required_capacity_lbs / 1000) / bearing_area
            allowable_bearing = 0.9 * fy

            if result.bearing_stress_ksi > allowable_bearing:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    check_type="bearing_stress_exceeded",
                    message=f"Bearing stress {result.bearing_stress_ksi:.1f} ksi > allowable {allowable_bearing:.1f} ksi",
                    suggestion="Increase plate thickness or hole diameter",
                    standard_reference="ASME BTH-1 3-3.2",
                ))
                result.critical_failures += 1
                result.failed += 1
            else:
                result.passed += 1
        else:
            result.failed += 1

        # Check 4: Tensile stress at throat
        result.total_checks += 1
        if lug.throat_width > 0:
            tensile_area = lug.throat_width * lug.plate_thickness

            if tensile_area > 0:
                result.tensile_stress_ksi = (result.required_capacity_lbs / 1000) / tensile_area
                allowable_tensile = 0.6 * fy

                if result.tensile_stress_ksi > allowable_tensile:
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        check_type="tensile_stress_exceeded",
                        message=f"Tensile stress {result.tensile_stress_ksi:.1f} ksi > allowable {allowable_tensile:.1f} ksi",
                        suggestion="Increase throat width or plate thickness",
                        standard_reference="ASME BTH-1 3-3.1",
                    ))
                    result.critical_failures += 1
                    result.failed += 1
                else:
                    result.passed += 1
            else:
                result.failed += 1
        else:
            result.passed += 1

        # Check 5: Weld capacity
        result.total_checks += 1
        if lug.weld_size > 0 and lug.weld_length > 0:
            # Fillet weld capacity (E70 electrode)
            throat = 0.707 * lug.weld_size
            weld_capacity = 0.6 * 70 * throat * lug.weld_length  # ksi × sq.in

            if (result.required_capacity_lbs / 1000) > weld_capacity * 0.75:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="weld_capacity_concern",
                    message=f"Weld may be undersized for load with design factor",
                    suggestion=f"Verify weld capacity: {weld_capacity * 0.75:.1f} kips φRn",
                    standard_reference="AWS D1.1",
                ))
                result.warnings += 1
            else:
                result.passed += 1
        else:
            result.passed += 1

        # Check 6: Minimum plate thickness
        result.total_checks += 1
        min_thickness = lug.hole_diameter * 0.5  # 0.5 × pin diameter minimum

        if lug.plate_thickness < min_thickness:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="plate_thickness_low",
                message=f"Plate thickness {lug.plate_thickness}\" less than 0.5 × pin diameter",
                suggestion=f"Consider {min_thickness:.3f}\" minimum thickness",
            ))
            result.warnings += 1
        else:
            result.passed += 1

        # Calculate lug capacity
        if shear_area > 0:
            shear_capacity = 0.4 * fy * shear_area * 1000
            bearing_capacity = 0.9 * fy * bearing_area * 1000 if bearing_area > 0 else 0
            tensile_capacity = 0.6 * fy * tensile_area * 1000 if lug.throat_width > 0 else 999999

            result.lug_capacity_lbs = min(shear_capacity, bearing_capacity, tensile_capacity) / result.design_factor

        return result

    def validate_rigging_arrangement(
        self,
        rigging: RiggingData
    ) -> RiggingValidationResult:
        """
        Validate complete rigging arrangement.

        Args:
            rigging: Rigging arrangement data

        Returns:
            Validation result
        """
        result = RiggingValidationResult()

        # Check 1: Minimum lift points
        result.total_checks += 1
        if len(rigging.lift_points) < 2:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="lift_points_insufficient",
                message=f"Only {len(rigging.lift_points)} lift point(s) specified",
                suggestion="Use minimum 2 lift points for stability",
            ))
            result.warnings += 1
        else:
            result.passed += 1

        # Check 2: CG within lift point polygon
        result.total_checks += 1
        if len(rigging.lift_points) >= 2:
            cg_ok = self._check_cg_within_lift_polygon(
                rigging.center_of_gravity,
                rigging.lift_points
            )

            if not cg_ok:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    check_type="cg_outside_lift_polygon",
                    message="Center of gravity is outside the lift point polygon",
                    suggestion="Reposition lift points to encompass CG",
                ))
                result.critical_failures += 1
                result.failed += 1
            else:
                result.passed += 1
        else:
            result.passed += 1

        # Check 3: Load distribution
        result.total_checks += 1
        if len(rigging.lift_points) >= 2:
            max_load_fraction = self._calculate_load_distribution(
                rigging.total_load_lbs,
                rigging.center_of_gravity,
                rigging.lift_points
            )

            if max_load_fraction > 0.5 and len(rigging.lift_points) >= 4:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="uneven_load_distribution",
                    message=f"Uneven load distribution - one point carries {max_load_fraction*100:.0f}% of load",
                    suggestion="Consider repositioning lift points for better balance",
                ))
                result.warnings += 1
            else:
                result.passed += 1
        else:
            result.passed += 1

        # Check 4: Sling angle considerations
        result.total_checks += 1
        # Calculate approximate sling angles based on geometry
        if len(rigging.lift_points) >= 2:
            # Simplified check - actual would calculate from hook height
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="sling_angle_reminder",
                message="Verify sling angles ≥45° from horizontal for safe rigging",
                suggestion="Sling angles <45° significantly reduce capacity",
                standard_reference="OSHA 1926.251",
            ))
            result.passed += 1
        else:
            result.passed += 1

        return result

    def _check_cg_within_lift_polygon(
        self,
        cg: Tuple[float, float, float],
        lift_points: List[Tuple[float, float, float]]
    ) -> bool:
        """Check if CG is within the polygon formed by lift points (plan view)."""
        if len(lift_points) < 2:
            return False

        # Simplified 2D check (plan view - x, y only)
        cg_x, cg_y = cg[0], cg[1]

        # Get lift point bounds
        xs = [p[0] for p in lift_points]
        ys = [p[1] for p in lift_points]

        # Simple bounding box check
        return (min(xs) <= cg_x <= max(xs)) and (min(ys) <= cg_y <= max(ys))

    def _calculate_load_distribution(
        self,
        total_load: float,
        cg: Tuple[float, float, float],
        lift_points: List[Tuple[float, float, float]]
    ) -> float:
        """Calculate approximate load fraction on most loaded point."""
        if len(lift_points) < 2:
            return 1.0

        # Simple distance-based approximation
        distances = []
        for lp in lift_points:
            dx = lp[0] - cg[0]
            dy = lp[1] - cg[1]
            dist = math.sqrt(dx*dx + dy*dy)
            distances.append(max(dist, 0.001))  # Avoid division by zero

        # Inverse distance weighting
        total_inv = sum(1/d for d in distances)
        fractions = [(1/d)/total_inv for d in distances]

        return max(fractions)

    def select_shackle(
        self,
        load_lbs: float,
        design_factor: float = 5.0
    ) -> Dict[str, Any]:
        """
        Select appropriate shackle for load.

        Args:
            load_lbs: Applied load in pounds
            design_factor: Safety factor (default 5.0 per ASME BTH-1)

        Returns:
            Dictionary with shackle recommendation
        """
        required_wll_tons = (load_lbs / 2000) * design_factor

        for size, wll in sorted(SHACKLE_CAPACITIES.items()):
            if wll >= required_wll_tons:
                return {
                    "shackle_size_in": size,
                    "wll_tons": wll,
                    "required_capacity_tons": required_wll_tons,
                    "utilization": required_wll_tons / wll,
                }

        return {
            "error": f"Load {load_lbs} lbs exceeds standard shackle capacities",
            "required_capacity_tons": required_wll_tons,
        }

    def to_dict(self, result: RiggingValidationResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "rigging",
            "total_checks": result.total_checks,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "critical_failures": result.critical_failures,
            "required_capacity_lbs": result.required_capacity_lbs,
            "design_factor": result.design_factor,
            "lug_capacity_lbs": result.lug_capacity_lbs,
            "stresses": {
                "shear_ksi": result.shear_stress_ksi,
                "bearing_ksi": result.bearing_stress_ksi,
                "tensile_ksi": result.tensile_stress_ksi,
            },
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
