"""
Hole Pattern Checker Adapter
============================
Verifies hole alignment between mating parts with tolerance checking.
Critical for ACHE/Fin Fan assemblies where bolt patterns must align.

Key Features:
- Cross-check mating part hole patterns (±1/16" tolerance)
- Verify standard vs non-standard hole sizes
- Check edge distances per AISC J3.4
- Validate bolt circle patterns
- Detect interference issues

References:
- AISC Table J3.3: Standard hole dimensions
- AISC Table J3.4: Minimum edge distances
- ACHE_CHECKLIST.md: Mating part verification

Usage:
    from agents.cad_agent.adapters.hole_pattern_checker import HolePatternChecker

    checker = HolePatternChecker()
    result = checker.verify_mating_patterns(part_a_holes, part_b_holes)
"""

import math
import logging
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

from .standards_db import (
    HOLE_SIZES,
    EDGE_DISTANCES,
    get_standard_hole,
    validate_hole_size,
    validate_edge_distance,
)

logger = logging.getLogger("cad_agent.hole-pattern-checker")


# =============================================================================
# CONSTANTS
# =============================================================================

# Default alignment tolerance (1/16")
DEFAULT_ALIGNMENT_TOLERANCE = 0.0625

# Minimum edge distance multiplier
MIN_EDGE_FACTOR = 1.5  # 1.5 × bolt diameter


# =============================================================================
# DATA MODELS
# =============================================================================

class HoleType(Enum):
    """Type of hole."""
    STANDARD = "standard"
    OVERSIZE = "oversize"
    SHORT_SLOT = "short_slot"
    LONG_SLOT = "long_slot"
    TAP = "tap"
    CLEARANCE = "clearance"
    UNKNOWN = "unknown"


class CheckStatus(Enum):
    """Status of a check."""
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"


@dataclass
class HoleLocation:
    """Hole with position information."""
    diameter: float
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    hole_type: HoleType = HoleType.STANDARD
    bolt_size: Optional[str] = None
    depth: Optional[float] = None
    quantity: int = 1
    label: str = ""


@dataclass
class PatternMatch:
    """Result of matching two holes."""
    hole_a: HoleLocation
    hole_b: HoleLocation
    distance: float
    is_aligned: bool
    message: str = ""


@dataclass
class AlignmentResult:
    """Result of pattern alignment check."""
    status: CheckStatus
    matches: list[PatternMatch] = field(default_factory=list)
    unmatched_a: list[HoleLocation] = field(default_factory=list)
    unmatched_b: list[HoleLocation] = field(default_factory=list)
    max_misalignment: float = 0.0
    message: str = ""


@dataclass
class EdgeDistanceResult:
    """Result of edge distance check."""
    status: CheckStatus
    hole: HoleLocation
    edge_distance: float
    min_required: float
    edge_type: str = "rolled"
    message: str = ""


@dataclass
class HoleStandardResult:
    """Result of hole standard check."""
    status: CheckStatus
    hole: HoleLocation
    expected_diameter: Optional[float] = None
    message: str = ""


@dataclass
class PatternCheckReport:
    """Complete hole pattern check report."""
    alignment: Optional[AlignmentResult] = None
    edge_distances: list[EdgeDistanceResult] = field(default_factory=list)
    hole_standards: list[HoleStandardResult] = field(default_factory=list)
    bolt_circle: Optional[dict] = None
    overall_status: CheckStatus = CheckStatus.PASS
    summary: str = ""


# =============================================================================
# HOLE PATTERN CHECKER
# =============================================================================

class HolePatternChecker:
    """
    Verify hole patterns for mating parts and AISC compliance.

    Features:
    - Mating part alignment verification
    - Standard hole size validation
    - Edge distance checking
    - Bolt circle pattern analysis
    """

    def __init__(
        self,
        alignment_tolerance: float = DEFAULT_ALIGNMENT_TOLERANCE,
    ):
        self.alignment_tolerance = alignment_tolerance

    # -------------------------------------------------------------------------
    # MATING PATTERN VERIFICATION
    # -------------------------------------------------------------------------

    def verify_mating_patterns(
        self,
        holes_a: list[HoleLocation],
        holes_b: list[HoleLocation],
        tolerance: Optional[float] = None,
    ) -> AlignmentResult:
        """
        Verify that hole patterns on two mating parts align.

        Args:
            holes_a: Holes from part A
            holes_b: Holes from part B
            tolerance: Alignment tolerance (default 1/16")

        Returns:
            AlignmentResult with match details
        """
        tolerance = tolerance or self.alignment_tolerance

        logger.info(f"Checking alignment: {len(holes_a)} holes vs {len(holes_b)} holes")

        matches = []
        unmatched_a = list(holes_a)
        unmatched_b = list(holes_b)
        max_misalignment = 0.0

        # Find matching holes
        for hole_a in holes_a:
            best_match = None
            best_distance = float('inf')

            for hole_b in holes_b:
                distance = self._calculate_distance(hole_a, hole_b)

                if distance < best_distance:
                    best_distance = distance
                    best_match = hole_b

            if best_match and best_distance <= tolerance:
                # Good match
                matches.append(PatternMatch(
                    hole_a=hole_a,
                    hole_b=best_match,
                    distance=best_distance,
                    is_aligned=True,
                    message=f"Aligned within {best_distance:.4f}\"",
                ))

                if hole_a in unmatched_a:
                    unmatched_a.remove(hole_a)
                if best_match in unmatched_b:
                    unmatched_b.remove(best_match)

            elif best_match:
                # Close but out of tolerance
                matches.append(PatternMatch(
                    hole_a=hole_a,
                    hole_b=best_match,
                    distance=best_distance,
                    is_aligned=False,
                    message=f"Misaligned by {best_distance:.4f}\" (tolerance {tolerance}\")",
                ))
                max_misalignment = max(max_misalignment, best_distance)

        # Determine overall status
        if all(m.is_aligned for m in matches) and not unmatched_a and not unmatched_b:
            status = CheckStatus.PASS
            message = f"All {len(matches)} holes aligned within {tolerance}\" tolerance"
        elif any(not m.is_aligned for m in matches):
            status = CheckStatus.FAIL
            misaligned_count = sum(1 for m in matches if not m.is_aligned)
            message = f"{misaligned_count} holes misaligned (max {max_misalignment:.4f}\")"
        elif unmatched_a or unmatched_b:
            status = CheckStatus.WARNING
            message = f"{len(unmatched_a)} unmatched in A, {len(unmatched_b)} unmatched in B"
        else:
            status = CheckStatus.PASS
            message = "Pattern alignment verified"

        return AlignmentResult(
            status=status,
            matches=matches,
            unmatched_a=unmatched_a,
            unmatched_b=unmatched_b,
            max_misalignment=max_misalignment,
            message=message,
        )

    # -------------------------------------------------------------------------
    # EDGE DISTANCE VERIFICATION
    # -------------------------------------------------------------------------

    def check_edge_distances(
        self,
        holes: list[HoleLocation],
        part_edges: list[tuple[float, float, float, float]],
        edge_type: str = "rolled",
    ) -> list[EdgeDistanceResult]:
        """
        Check edge distances for all holes.

        Args:
            holes: List of holes to check
            part_edges: List of edges as (x1, y1, x2, y2) line segments
            edge_type: "rolled" or "sheared" (affects minimum distance)

        Returns:
            List of EdgeDistanceResult for each hole
        """
        results = []

        for hole in holes:
            # Find minimum distance to any edge
            min_edge_dist = float('inf')

            for edge in part_edges:
                dist = self._point_to_line_distance(
                    hole.x, hole.y,
                    edge[0], edge[1], edge[2], edge[3]
                )
                min_edge_dist = min(min_edge_dist, dist)

            # Determine bolt size from hole diameter
            bolt_size = hole.bolt_size or self._infer_bolt_size(hole.diameter)

            # Get minimum required edge distance
            min_required = None
            if bolt_size:
                _, msg = validate_edge_distance(min_edge_dist, bolt_size, edge_type)
                edge_data = EDGE_DISTANCES.get(bolt_size.replace('"', '').strip())
                if edge_data:
                    min_required = edge_data.get(f"min_{edge_type}", 0)

            if min_required is None:
                # Fallback: 1.5 × hole diameter
                min_required = hole.diameter * MIN_EDGE_FACTOR

            # Determine status
            if min_edge_dist >= min_required:
                status = CheckStatus.PASS
                message = f"Edge distance {min_edge_dist:.3f}\" >= min {min_required:.3f}\""
            elif min_edge_dist >= min_required * 0.9:
                status = CheckStatus.WARNING
                message = f"Edge distance {min_edge_dist:.3f}\" near limit (min {min_required:.3f}\")"
            else:
                status = CheckStatus.FAIL
                message = f"Edge distance {min_edge_dist:.3f}\" < min {min_required:.3f}\""

            results.append(EdgeDistanceResult(
                status=status,
                hole=hole,
                edge_distance=min_edge_dist,
                min_required=min_required,
                edge_type=edge_type,
                message=message,
            ))

        return results

    # -------------------------------------------------------------------------
    # HOLE STANDARD VERIFICATION
    # -------------------------------------------------------------------------

    def verify_hole_standards(
        self,
        holes: list[HoleLocation],
    ) -> list[HoleStandardResult]:
        """
        Verify all holes use standard sizes per AISC.

        Args:
            holes: List of holes to check

        Returns:
            List of HoleStandardResult for each hole
        """
        results = []

        for hole in holes:
            bolt_size = hole.bolt_size or self._infer_bolt_size(hole.diameter)

            if not bolt_size:
                results.append(HoleStandardResult(
                    status=CheckStatus.WARNING,
                    hole=hole,
                    message=f"Cannot determine bolt size for {hole.diameter}\" hole",
                ))
                continue

            is_valid, msg = validate_hole_size(hole.diameter, bolt_size)
            expected = get_standard_hole(bolt_size)

            if is_valid:
                status = CheckStatus.PASS
            else:
                status = CheckStatus.FAIL

            results.append(HoleStandardResult(
                status=status,
                hole=hole,
                expected_diameter=expected,
                message=msg,
            ))

        return results

    # -------------------------------------------------------------------------
    # BOLT CIRCLE ANALYSIS
    # -------------------------------------------------------------------------

    def analyze_bolt_circle(
        self,
        holes: list[HoleLocation],
        expected_pcd: Optional[float] = None,
        expected_count: Optional[int] = None,
    ) -> dict:
        """
        Analyze a bolt circle pattern.

        Args:
            holes: Holes that should form a bolt circle
            expected_pcd: Expected pitch circle diameter
            expected_count: Expected number of holes

        Returns:
            Analysis dict with PCD, spacing, and deviations
        """
        if len(holes) < 2:
            return {"error": "Need at least 2 holes for bolt circle analysis"}

        # Find centroid
        cx = sum(h.x for h in holes) / len(holes)
        cy = sum(h.y for h in holes) / len(holes)

        # Calculate radii from center
        radii = []
        for h in holes:
            r = math.sqrt((h.x - cx) ** 2 + (h.y - cy) ** 2)
            radii.append(r)

        avg_radius = sum(radii) / len(radii)
        pcd = avg_radius * 2  # Pitch circle diameter

        # Calculate angular spacing
        angles = []
        for h in holes:
            angle = math.atan2(h.y - cy, h.x - cx)
            angles.append(math.degrees(angle))

        angles.sort()

        # Calculate spacing between adjacent holes
        spacings = []
        for i in range(len(angles)):
            next_i = (i + 1) % len(angles)
            spacing = angles[next_i] - angles[i]
            if spacing < 0:
                spacing += 360
            spacings.append(spacing)

        avg_spacing = 360 / len(holes) if holes else 0
        max_spacing_dev = max(abs(s - avg_spacing) for s in spacings) if spacings else 0

        # Check against expected values
        status = CheckStatus.PASS
        messages = []

        if expected_pcd:
            pcd_diff = abs(pcd - expected_pcd)
            if pcd_diff > 0.125:  # 1/8" tolerance
                status = CheckStatus.FAIL
                messages.append(f"PCD {pcd:.3f}\" differs from expected {expected_pcd}\"")
            elif pcd_diff > 0.0625:  # 1/16" warning
                status = CheckStatus.WARNING
                messages.append(f"PCD {pcd:.3f}\" near expected {expected_pcd}\"")

        if expected_count and len(holes) != expected_count:
            status = CheckStatus.FAIL
            messages.append(f"Found {len(holes)} holes, expected {expected_count}")

        # Check radius consistency
        radius_dev = max(abs(r - avg_radius) for r in radii)
        if radius_dev > 0.0625:  # 1/16"
            if status != CheckStatus.FAIL:
                status = CheckStatus.WARNING
            messages.append(f"Radius deviation {radius_dev:.4f}\"")

        return {
            "status": status.value,
            "center": {"x": cx, "y": cy},
            "pcd": pcd,
            "hole_count": len(holes),
            "avg_spacing_degrees": avg_spacing,
            "max_spacing_deviation": max_spacing_dev,
            "radius_deviation": radius_dev,
            "messages": messages,
        }

    # -------------------------------------------------------------------------
    # FULL PATTERN CHECK
    # -------------------------------------------------------------------------

    def full_pattern_check(
        self,
        holes: list[HoleLocation],
        mating_holes: Optional[list[HoleLocation]] = None,
        part_edges: Optional[list[tuple[float, float, float, float]]] = None,
        bolt_circle_expected: Optional[dict] = None,
    ) -> PatternCheckReport:
        """
        Run comprehensive hole pattern checks.

        Args:
            holes: Primary holes to check
            mating_holes: Holes from mating part (optional)
            part_edges: Edge segments for edge distance check
            bolt_circle_expected: Expected bolt circle params

        Returns:
            Complete PatternCheckReport
        """
        report = PatternCheckReport()
        issues = []

        # Alignment check
        if mating_holes:
            report.alignment = self.verify_mating_patterns(holes, mating_holes)
            if report.alignment.status == CheckStatus.FAIL:
                issues.append("Hole alignment failed")
            elif report.alignment.status == CheckStatus.WARNING:
                issues.append("Hole alignment warning")

        # Edge distance check
        if part_edges:
            report.edge_distances = self.check_edge_distances(holes, part_edges)
            failed = sum(1 for r in report.edge_distances if r.status == CheckStatus.FAIL)
            if failed:
                issues.append(f"{failed} edge distance failures")

        # Hole standards check
        report.hole_standards = self.verify_hole_standards(holes)
        non_standard = sum(1 for r in report.hole_standards if r.status == CheckStatus.FAIL)
        if non_standard:
            issues.append(f"{non_standard} non-standard holes")

        # Bolt circle check
        if bolt_circle_expected:
            report.bolt_circle = self.analyze_bolt_circle(
                holes,
                expected_pcd=bolt_circle_expected.get("pcd"),
                expected_count=bolt_circle_expected.get("count"),
            )
            if report.bolt_circle.get("status") == "fail":
                issues.append("Bolt circle check failed")

        # Determine overall status
        if any("failed" in i or "failure" in i for i in issues):
            report.overall_status = CheckStatus.FAIL
        elif issues:
            report.overall_status = CheckStatus.WARNING
        else:
            report.overall_status = CheckStatus.PASS

        report.summary = "; ".join(issues) if issues else "All hole pattern checks passed"

        return report

    # -------------------------------------------------------------------------
    # HELPER METHODS
    # -------------------------------------------------------------------------

    def _calculate_distance(self, hole_a: HoleLocation, hole_b: HoleLocation) -> float:
        """Calculate 3D distance between two holes."""
        return math.sqrt(
            (hole_a.x - hole_b.x) ** 2 +
            (hole_a.y - hole_b.y) ** 2 +
            (hole_a.z - hole_b.z) ** 2
        )

    def _point_to_line_distance(
        self,
        px: float, py: float,
        x1: float, y1: float, x2: float, y2: float,
    ) -> float:
        """Calculate distance from point to line segment."""
        # Vector from line start to point
        dx = x2 - x1
        dy = y2 - y1

        if dx == 0 and dy == 0:
            # Line is a point
            return math.sqrt((px - x1) ** 2 + (py - y1) ** 2)

        # Parameter t for closest point on line
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))

        # Closest point on line segment
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy

        return math.sqrt((px - closest_x) ** 2 + (py - closest_y) ** 2)

    def _infer_bolt_size(self, hole_diameter: float) -> Optional[str]:
        """Infer bolt size from hole diameter."""
        # Standard hole = bolt + 1/16"
        bolt_diameter = hole_diameter - 0.0625

        # Common bolt sizes
        bolt_sizes = ["1/2", "5/8", "3/4", "7/8", "1", "1-1/8", "1-1/4"]
        bolt_decimals = [0.5, 0.625, 0.75, 0.875, 1.0, 1.125, 1.25]

        for size, decimal in zip(bolt_sizes, bolt_decimals):
            if abs(bolt_diameter - decimal) < 0.05:
                return size

        return None


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "HolePatternChecker",
    "HoleLocation",
    "HoleType",
    "AlignmentResult",
    "EdgeDistanceResult",
    "HoleStandardResult",
    "PatternMatch",
    "PatternCheckReport",
    "CheckStatus",
]
