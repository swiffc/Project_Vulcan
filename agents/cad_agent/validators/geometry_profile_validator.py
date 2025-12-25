"""
Geometry & Profile Validator
=============================
Validates geometry features: corner radii, cope dimensions, notch stress, web openings.

Phase 25 - Drawing Checker Standards Completion
"""

import logging
import math
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.geometry")


# Minimum inside corner radii for cutting processes (inches)
MIN_CORNER_RADII = {
    "plasma": 0.125,      # 1/8" min for plasma
    "laser": 0.020,       # 0.020" for laser (material thickness dependent)
    "waterjet": 0.030,    # 0.030" for waterjet
    "punch": 0.062,       # 1/16" for punching
    "mill": 0.125,        # Depends on end mill size
    "flame": 0.250,       # 1/4" for oxy-fuel
}

# Cope dimension requirements per AISC
# Cope depth should not exceed 2 × beam depth or special analysis required
COPE_DEPTH_RATIO_MAX = 0.2  # Max cope depth as ratio of beam depth

# Minimum cope length for weld access (inches)
MIN_COPE_LENGTH = 1.5

# Standard cope corner radius (inches)
STANDARD_COPE_RADIUS = 0.5

# Notch stress concentration factors (Kt) - simplified
NOTCH_KT_FACTORS = {
    "sharp": 3.0,         # Sharp 90° notch
    "small_radius": 2.5,  # Small fillet radius
    "medium_radius": 2.0, # Medium fillet
    "large_radius": 1.5,  # Large generous fillet
}

# Web opening limits per AISC Design Guide 2
WEB_OPENING_MAX_DEPTH_RATIO = 0.7  # Max opening depth / beam depth
WEB_OPENING_MIN_EDGE_DISTANCE = 2.0  # Min distance from flange (× tw)


@dataclass
class CornerData:
    """Corner geometry data."""
    radius: float = 0.0  # Inside corner radius
    angle_deg: float = 90.0  # Corner angle
    cutting_process: str = "plasma"
    location: str = ""


@dataclass
class CopeData:
    """Beam cope data."""
    cope_depth_in: float = 0.0
    cope_length_in: float = 0.0
    corner_radius_in: float = 0.0
    beam_depth_in: float = 0.0
    is_top_flange: bool = True
    has_weld_access: bool = True


@dataclass
class NotchData:
    """Notch/stress riser data."""
    notch_depth_in: float = 0.0
    notch_radius_in: float = 0.0
    notch_angle_deg: float = 90.0
    is_fatigue_critical: bool = False
    location: str = ""


@dataclass
class WebOpeningData:
    """Web opening data."""
    opening_depth_in: float = 0.0
    opening_length_in: float = 0.0
    beam_depth_in: float = 0.0
    web_thickness_in: float = 0.0
    distance_to_flange_in: float = 0.0
    has_reinforcement: bool = False
    opening_shape: str = "rectangular"  # rectangular, circular


@dataclass
class GeometryValidationResult:
    """Geometry validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

    # Calculated values
    min_required_radius: Optional[float] = None
    stress_concentration_factor: Optional[float] = None
    max_opening_depth: Optional[float] = None


class GeometryProfileValidator:
    """
    Validates geometry and profile features.

    Checks:
    1. Inside corner radii for cutting process
    2. Cope dimensions and access
    3. Notch stress concentration
    4. Web openings per AISC DG2
    """

    def __init__(self):
        pass

    def validate_corner_radius(
        self,
        corner: CornerData,
    ) -> GeometryValidationResult:
        """
        Validate inside corner radius for cutting process.

        Args:
            corner: Corner geometry data

        Returns:
            Validation result
        """
        result = GeometryValidationResult()
        result.total_checks += 1

        process = corner.cutting_process.lower()
        min_radius = MIN_CORNER_RADII.get(process, 0.125)
        result.min_required_radius = min_radius

        if corner.radius < min_radius:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="corner_radius",
                message=f"Corner radius {corner.radius}\" < min {min_radius}\" for {process}",
                location=corner.location,
                suggestion=f"Increase corner radius to ≥{min_radius}\" or change cutting process",
            ))
        else:
            result.passed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="corner_radius",
                message=f"Corner radius {corner.radius}\" OK for {process} (min {min_radius}\")",
                location=corner.location,
            ))

        # Check for very small radii that may cause tool wear
        if corner.radius < 0.0625 and process in ["mill", "punch"]:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="corner_radius_tooling",
                message=f"Small radius {corner.radius}\" may cause rapid tool wear",
                suggestion="Consider larger radius for production efficiency",
            ))

        return result

    def validate_cope(
        self,
        cope: CopeData,
    ) -> GeometryValidationResult:
        """
        Validate beam cope dimensions.

        Args:
            cope: Cope geometry data

        Returns:
            Validation result
        """
        result = GeometryValidationResult()

        # Check cope depth ratio
        result.total_checks += 1
        if cope.beam_depth_in > 0:
            depth_ratio = cope.cope_depth_in / cope.beam_depth_in

            if depth_ratio > COPE_DEPTH_RATIO_MAX:
                result.failed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="cope_depth",
                    message=f"Cope depth ratio {depth_ratio:.2f} > max {COPE_DEPTH_RATIO_MAX}",
                    suggestion="Reduce cope depth or perform special analysis per AISC",
                    standard_reference="AISC Design Guide 2",
                ))
            else:
                result.passed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="cope_depth",
                    message=f"Cope depth ratio {depth_ratio:.2f} ≤ {COPE_DEPTH_RATIO_MAX} OK",
                    standard_reference="AISC Design Guide 2",
                ))

        # Check cope length for weld access
        result.total_checks += 1
        if cope.cope_length_in < MIN_COPE_LENGTH:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="cope_length",
                message=f"Cope length {cope.cope_length_in}\" < recommended {MIN_COPE_LENGTH}\"",
                suggestion="Increase cope length for adequate weld access",
            ))
        else:
            result.passed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="cope_length",
                message=f"Cope length {cope.cope_length_in}\" provides weld access",
            ))

        # Check cope corner radius (stress riser)
        result.total_checks += 1
        if cope.corner_radius_in < STANDARD_COPE_RADIUS:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="cope_corner_radius",
                message=f"Cope corner radius {cope.corner_radius_in}\" < standard {STANDARD_COPE_RADIUS}\"",
                suggestion=f"Use {STANDARD_COPE_RADIUS}\" min radius to reduce stress concentration",
            ))
        else:
            result.passed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="cope_corner_radius",
                message=f"Cope corner radius {cope.corner_radius_in}\" OK",
            ))

        return result

    def validate_notch(
        self,
        notch: NotchData,
    ) -> GeometryValidationResult:
        """
        Validate notch stress concentration.

        Args:
            notch: Notch geometry data

        Returns:
            Validation result
        """
        result = GeometryValidationResult()
        result.total_checks += 1

        # Calculate stress concentration factor based on radius
        if notch.notch_radius_in <= 0.0:
            kt = NOTCH_KT_FACTORS["sharp"]
            radius_class = "sharp"
        elif notch.notch_radius_in < 0.125:
            kt = NOTCH_KT_FACTORS["small_radius"]
            radius_class = "small_radius"
        elif notch.notch_radius_in < 0.25:
            kt = NOTCH_KT_FACTORS["medium_radius"]
            radius_class = "medium_radius"
        else:
            kt = NOTCH_KT_FACTORS["large_radius"]
            radius_class = "large_radius"

        result.stress_concentration_factor = kt

        # Sharp notches are problematic in fatigue
        if notch.is_fatigue_critical and kt > 2.0:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="notch_stress",
                message=f"High stress concentration Kt={kt:.1f} in fatigue-critical location",
                location=notch.location,
                suggestion="Add generous fillet radius (≥0.25\") to reduce stress concentration",
            ))
        elif kt > 2.5:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="notch_stress",
                message=f"High stress concentration Kt={kt:.1f} ({radius_class})",
                location=notch.location,
                suggestion="Consider adding fillet radius to reduce stress",
            ))
        else:
            result.passed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="notch_stress",
                message=f"Stress concentration Kt={kt:.1f} acceptable",
                location=notch.location,
            ))

        return result

    def validate_web_opening(
        self,
        opening: WebOpeningData,
    ) -> GeometryValidationResult:
        """
        Validate web opening per AISC Design Guide 2.

        Args:
            opening: Web opening data

        Returns:
            Validation result
        """
        result = GeometryValidationResult()

        if opening.beam_depth_in <= 0:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="web_opening_data",
                message="Beam depth not specified for web opening check",
            ))
            return result

        # Check opening depth ratio
        result.total_checks += 1
        depth_ratio = opening.opening_depth_in / opening.beam_depth_in
        max_opening = WEB_OPENING_MAX_DEPTH_RATIO * opening.beam_depth_in
        result.max_opening_depth = max_opening

        if depth_ratio > WEB_OPENING_MAX_DEPTH_RATIO:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="web_opening_depth",
                message=f"Opening depth {opening.opening_depth_in}\" ({depth_ratio:.0%}) > max 70% of beam depth",
                suggestion=f"Reduce opening to ≤{max_opening:.2f}\" or add reinforcement",
                standard_reference="AISC Design Guide 2",
            ))
        else:
            result.passed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="web_opening_depth",
                message=f"Opening depth {opening.opening_depth_in}\" ({depth_ratio:.0%}) OK",
                standard_reference="AISC Design Guide 2",
            ))

        # Check edge distance to flange
        result.total_checks += 1
        if opening.web_thickness_in > 0:
            min_edge = WEB_OPENING_MIN_EDGE_DISTANCE * opening.web_thickness_in

            if opening.distance_to_flange_in < min_edge:
                result.failed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="web_opening_edge",
                    message=f"Opening too close to flange: {opening.distance_to_flange_in}\" < min {min_edge:.2f}\"",
                    suggestion="Move opening away from flange or add reinforcement",
                    standard_reference="AISC Design Guide 2",
                ))
            else:
                result.passed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="web_opening_edge",
                    message=f"Edge distance {opening.distance_to_flange_in}\" ≥ {min_edge:.2f}\" OK",
                ))

        # Check if reinforcement is needed for large openings
        if depth_ratio > 0.5 and not opening.has_reinforcement:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="web_opening_reinforcement",
                message="Large web opening may require reinforcement",
                suggestion="Add horizontal stiffeners or ring reinforcement per AISC DG2",
            ))

        return result

    def validate_all(
        self,
        corners: List[CornerData] = None,
        copes: List[CopeData] = None,
        notches: List[NotchData] = None,
        openings: List[WebOpeningData] = None,
    ) -> GeometryValidationResult:
        """
        Run all geometry validations.

        Args:
            corners: List of corner data
            copes: List of cope data
            notches: List of notch data
            openings: List of web opening data

        Returns:
            Combined validation result
        """
        result = GeometryValidationResult()

        for corner in (corners or []):
            r = self.validate_corner_radius(corner)
            result.total_checks += r.total_checks
            result.passed += r.passed
            result.failed += r.failed
            result.warnings += r.warnings
            result.issues.extend(r.issues)

        for cope in (copes or []):
            r = self.validate_cope(cope)
            result.total_checks += r.total_checks
            result.passed += r.passed
            result.failed += r.failed
            result.warnings += r.warnings
            result.issues.extend(r.issues)

        for notch in (notches or []):
            r = self.validate_notch(notch)
            result.total_checks += r.total_checks
            result.passed += r.passed
            result.failed += r.failed
            result.warnings += r.warnings
            result.issues.extend(r.issues)

        for opening in (openings or []):
            r = self.validate_web_opening(opening)
            result.total_checks += r.total_checks
            result.passed += r.passed
            result.failed += r.failed
            result.warnings += r.warnings
            result.issues.extend(r.issues)

        return result

    def to_dict(self, result: GeometryValidationResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "geometry_profile",
            "total_checks": result.total_checks,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "calculations": {
                "min_required_radius_in": result.min_required_radius,
                "stress_concentration_factor": result.stress_concentration_factor,
                "max_opening_depth_in": result.max_opening_depth,
            },
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
