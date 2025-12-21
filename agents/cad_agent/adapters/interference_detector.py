"""
Interference Detection Adapter for CAD Assemblies
==================================================
Detects geometric interference and clearance violations in assemblies.

Use Cases:
- Fan ring vs blade tip clearance (API 661)
- Nozzle vs structural steel conflicts
- Piping routing clearances
- Motor/drive accessibility
- Platform/ladder headroom
- Tube bundle insertion path

This adapter works with:
1. SolidWorks assemblies (via COM)
2. DXF/DWG 2D drawings (via ezdxf)
3. Extracted dimensions from PDFs

References:
- API 661 Section 4.4 - Clearances
- OSHA 1910.23 - Platform headroom
- ASME B31.3 - Piping clearances

Usage:
    from agents.cad_agent.adapters.interference_detector import (
        check_assembly_interference,
        check_2d_clearances,
        check_fan_ring_clearance,
    )
"""

from typing import Optional
from dataclasses import dataclass, field
from enum import Enum
import math


# =============================================================================
# ENUMS & DATA CLASSES
# =============================================================================

class SeverityLevel(Enum):
    """Severity of interference or clearance violation."""
    CRITICAL = "critical"    # Hard interference - parts overlap
    WARNING = "warning"      # Clearance below minimum
    INFO = "info"            # Clearance close to minimum


class ClearanceType(Enum):
    """Types of clearance requirements."""
    FAN_TIP = "fan_tip"              # Fan blade to shroud
    TUBE_INSERTION = "tube_insertion"  # Tube bundle removal path
    MAINTENANCE = "maintenance"        # Access for maintenance
    WALKWAY = "walkway"               # Personnel access
    PIPING = "piping"                 # Pipe-to-pipe
    STRUCTURAL = "structural"          # Steel member clearance
    HEADROOM = "headroom"             # Vertical clearance
    NOZZLE = "nozzle"                 # Nozzle projection


@dataclass
class BoundingBox:
    """3D bounding box for a component."""
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_min: float = 0.0
    z_max: float = 0.0

    @property
    def width(self) -> float:
        return self.x_max - self.x_min

    @property
    def height(self) -> float:
        return self.y_max - self.y_min

    @property
    def depth(self) -> float:
        return self.z_max - self.z_min

    @property
    def center(self) -> tuple[float, float, float]:
        return (
            (self.x_min + self.x_max) / 2,
            (self.y_min + self.y_max) / 2,
            (self.z_min + self.z_max) / 2,
        )


@dataclass
class Circle2D:
    """2D circle representation (for fan rings, bolt circles, etc.)."""
    center_x: float
    center_y: float
    radius: float

    @property
    def diameter(self) -> float:
        return self.radius * 2


@dataclass
class Component:
    """Assembly component with geometry."""
    name: str
    part_number: str
    bounds: BoundingBox
    component_type: str = "generic"  # fan, tube_bundle, platform, pipe, etc.


@dataclass
class InterferenceResult:
    """Result of interference detection."""
    has_interference: bool
    component_a: str
    component_b: str
    overlap_distance: float  # Negative = interference, positive = clearance
    severity: SeverityLevel
    location: tuple[float, float, float]
    message: str


@dataclass
class ClearanceResult:
    """Result of clearance check."""
    passes: bool
    clearance_type: ClearanceType
    measured: float
    required: float
    severity: SeverityLevel
    location: str
    message: str


@dataclass
class AssemblyAnalysis:
    """Complete assembly interference analysis."""
    assembly_name: str
    total_components: int
    interferences: list[InterferenceResult] = field(default_factory=list)
    clearance_violations: list[ClearanceResult] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def has_critical_issues(self) -> bool:
        critical_interferences = [i for i in self.interferences if i.severity == SeverityLevel.CRITICAL]
        critical_clearances = [c for c in self.clearance_violations if c.severity == SeverityLevel.CRITICAL]
        return len(critical_interferences) > 0 or len(critical_clearances) > 0


# =============================================================================
# MINIMUM CLEARANCE REQUIREMENTS
# =============================================================================

# API 661 / Industry standard clearances (inches)
MIN_CLEARANCES: dict[ClearanceType, float] = {
    ClearanceType.FAN_TIP: 0.5,          # Fan blade to shroud ring (depends on dia)
    ClearanceType.TUBE_INSERTION: 24.0,   # Clear path for bundle
    ClearanceType.MAINTENANCE: 18.0,      # Tool access
    ClearanceType.WALKWAY: 30.0,          # Platform width
    ClearanceType.PIPING: 1.0,            # Between parallel pipes
    ClearanceType.STRUCTURAL: 2.0,        # Around structural members
    ClearanceType.HEADROOM: 78.0,         # 6'-6" minimum
    ClearanceType.NOZZLE: 1.0,            # Flange projection
}

# API 661 fan tip clearances by diameter (inches)
FAN_TIP_CLEARANCE_BY_DIA: dict[str, tuple[float, float]] = {
    # Fan diameter range: (min clearance, max clearance)
    "4-5ft": (0.250, 0.375),
    "6-8ft": (0.375, 0.500),
    "9-12ft": (0.500, 0.625),
    "13-18ft": (0.625, 0.750),
    "19-28ft": (0.750, 1.000),
    ">28ft": (1.000, 1.250),
}


# =============================================================================
# BOUNDING BOX INTERFERENCE
# =============================================================================

def check_box_overlap(box_a: BoundingBox, box_b: BoundingBox) -> tuple[bool, float]:
    """
    Check if two bounding boxes overlap.

    Returns:
        Tuple of (overlaps, min_distance)
        - If overlaps is True, min_distance is the overlap depth (negative)
        - If overlaps is False, min_distance is the gap (positive)
    """
    # Calculate overlaps in each axis
    x_overlap = min(box_a.x_max, box_b.x_max) - max(box_a.x_min, box_b.x_min)
    y_overlap = min(box_a.y_max, box_b.y_max) - max(box_a.y_min, box_b.y_min)
    z_overlap = min(box_a.z_max, box_b.z_max) - max(box_a.z_min, box_b.z_min)

    # If all three overlaps are positive, boxes intersect
    if x_overlap > 0 and y_overlap > 0 and z_overlap > 0:
        # Return the minimum overlap as the interference depth
        min_overlap = min(x_overlap, y_overlap, z_overlap)
        return True, -min_overlap

    # Find the closest faces
    gaps = []
    if x_overlap <= 0:
        gaps.append(-x_overlap)
    if y_overlap <= 0:
        gaps.append(-y_overlap)
    if z_overlap <= 0:
        gaps.append(-z_overlap)

    if gaps:
        return False, min(gaps)

    return False, 0.0


def check_2d_box_overlap(box_a: BoundingBox, box_b: BoundingBox) -> tuple[bool, float]:
    """
    Check 2D bounding box overlap (X-Y plane only).

    Returns:
        Tuple of (overlaps, min_distance)
    """
    x_overlap = min(box_a.x_max, box_b.x_max) - max(box_a.x_min, box_b.x_min)
    y_overlap = min(box_a.y_max, box_b.y_max) - max(box_a.y_min, box_b.y_min)

    if x_overlap > 0 and y_overlap > 0:
        return True, -min(x_overlap, y_overlap)

    gaps = []
    if x_overlap <= 0:
        gaps.append(-x_overlap)
    if y_overlap <= 0:
        gaps.append(-y_overlap)

    return False, min(gaps) if gaps else 0.0


# =============================================================================
# CIRCLE CLEARANCE CHECKS
# =============================================================================

def check_circle_clearance(
    outer: Circle2D,
    inner: Circle2D,
    min_clearance: float
) -> ClearanceResult:
    """
    Check clearance between concentric circles (e.g., fan blade to shroud).

    Args:
        outer: Outer circle (e.g., fan ring)
        inner: Inner circle (e.g., blade tip circle)
        min_clearance: Required clearance

    Returns:
        ClearanceResult
    """
    # Calculate center offset
    center_dist = math.sqrt(
        (outer.center_x - inner.center_x) ** 2 +
        (outer.center_y - inner.center_y) ** 2
    )

    # Radial clearance considering offset
    # Minimum clearance occurs at the point closest to the outer ring
    actual_clearance = outer.radius - inner.radius - center_dist

    if actual_clearance < 0:
        return ClearanceResult(
            passes=False,
            clearance_type=ClearanceType.FAN_TIP,
            measured=actual_clearance,
            required=min_clearance,
            severity=SeverityLevel.CRITICAL,
            location=f"Inner circle extends beyond outer",
            message=f"INTERFERENCE: Inner circle {inner.diameter:.2f}\" exceeds outer {outer.diameter:.2f}\""
        )

    if actual_clearance < min_clearance:
        return ClearanceResult(
            passes=False,
            clearance_type=ClearanceType.FAN_TIP,
            measured=actual_clearance,
            required=min_clearance,
            severity=SeverityLevel.WARNING if actual_clearance > min_clearance * 0.5 else SeverityLevel.CRITICAL,
            location=f"Radial clearance",
            message=f"Clearance {actual_clearance:.3f}\" below min {min_clearance:.3f}\""
        )

    return ClearanceResult(
        passes=True,
        clearance_type=ClearanceType.FAN_TIP,
        measured=actual_clearance,
        required=min_clearance,
        severity=SeverityLevel.INFO,
        location=f"Radial clearance",
        message=f"Clearance {actual_clearance:.3f}\" OK (min {min_clearance:.3f}\")"
    )


def get_fan_tip_clearance_range(fan_diameter_ft: float) -> tuple[float, float]:
    """
    Get acceptable fan tip clearance range per API 661.

    Args:
        fan_diameter_ft: Fan diameter in feet

    Returns:
        Tuple of (min_clearance, max_clearance) in inches
    """
    if fan_diameter_ft <= 5:
        return (0.250, 0.375)
    elif fan_diameter_ft <= 8:
        return (0.375, 0.500)
    elif fan_diameter_ft <= 12:
        return (0.500, 0.625)
    elif fan_diameter_ft <= 18:
        return (0.625, 0.750)
    elif fan_diameter_ft <= 28:
        return (0.750, 1.000)
    else:
        return (1.000, 1.250)


def check_fan_ring_clearance(
    ring_id: float,
    blade_diameter: float,
    fan_diameter_ft: Optional[float] = None
) -> ClearanceResult:
    """
    Check fan blade to ring clearance per API 661.

    Args:
        ring_id: Fan ring inside diameter (inches)
        blade_diameter: Fan blade tip-to-tip diameter (inches)
        fan_diameter_ft: Optional fan diameter for clearance lookup

    Returns:
        ClearanceResult
    """
    # Calculate actual clearance
    radial_clearance = (ring_id - blade_diameter) / 2

    # Determine required clearance
    if fan_diameter_ft:
        min_clear, max_clear = get_fan_tip_clearance_range(fan_diameter_ft)
    else:
        # Estimate from blade diameter
        est_dia_ft = blade_diameter / 12
        min_clear, max_clear = get_fan_tip_clearance_range(est_dia_ft)

    if radial_clearance < 0:
        return ClearanceResult(
            passes=False,
            clearance_type=ClearanceType.FAN_TIP,
            measured=radial_clearance,
            required=min_clear,
            severity=SeverityLevel.CRITICAL,
            location="Fan ring",
            message=f"INTERFERENCE: Blade {blade_diameter:.2f}\" exceeds ring ID {ring_id:.2f}\""
        )

    if radial_clearance < min_clear:
        return ClearanceResult(
            passes=False,
            clearance_type=ClearanceType.FAN_TIP,
            measured=radial_clearance,
            required=min_clear,
            severity=SeverityLevel.WARNING,
            location="Fan ring",
            message=f"Tip clearance {radial_clearance:.3f}\" below min {min_clear:.3f}\""
        )

    if radial_clearance > max_clear:
        return ClearanceResult(
            passes=True,
            clearance_type=ClearanceType.FAN_TIP,
            measured=radial_clearance,
            required=min_clear,
            severity=SeverityLevel.WARNING,
            location="Fan ring",
            message=f"Tip clearance {radial_clearance:.3f}\" exceeds recommended max {max_clear:.3f}\" (reduced efficiency)"
        )

    return ClearanceResult(
        passes=True,
        clearance_type=ClearanceType.FAN_TIP,
        measured=radial_clearance,
        required=min_clear,
        severity=SeverityLevel.INFO,
        location="Fan ring",
        message=f"Tip clearance {radial_clearance:.3f}\" OK (range {min_clear:.3f}\"-{max_clear:.3f}\")"
    )


# =============================================================================
# TUBE BUNDLE INSERTION PATH
# =============================================================================

def check_tube_bundle_path(
    bundle_envelope: BoundingBox,
    obstacles: list[BoundingBox],
    insertion_direction: str = "+X"
) -> list[InterferenceResult]:
    """
    Check if tube bundle can be extracted without hitting obstacles.

    Args:
        bundle_envelope: Bounding box of tube bundle
        obstacles: List of obstacle bounding boxes (structural steel, platforms, etc.)
        insertion_direction: Direction of insertion (+X, -X, +Y, -Y)

    Returns:
        List of InterferenceResult for any collisions
    """
    results = []

    # Extend bundle envelope in insertion direction
    extended = BoundingBox(
        x_min=bundle_envelope.x_min,
        x_max=bundle_envelope.x_max,
        y_min=bundle_envelope.y_min,
        y_max=bundle_envelope.y_max,
        z_min=bundle_envelope.z_min,
        z_max=bundle_envelope.z_max
    )

    # Extend by a large amount in the insertion direction
    extension = 1000.0  # Arbitrary large extension

    if insertion_direction == "+X":
        extended.x_max += extension
    elif insertion_direction == "-X":
        extended.x_min -= extension
    elif insertion_direction == "+Y":
        extended.y_max += extension
    elif insertion_direction == "-Y":
        extended.y_min -= extension

    # Check against each obstacle
    for i, obstacle in enumerate(obstacles):
        overlaps, dist = check_box_overlap(extended, obstacle)

        if overlaps:
            results.append(InterferenceResult(
                has_interference=True,
                component_a="Tube Bundle Path",
                component_b=f"Obstacle_{i}",
                overlap_distance=dist,
                severity=SeverityLevel.CRITICAL,
                location=obstacle.center,
                message=f"Tube bundle path blocked by obstacle (overlap {abs(dist):.2f}\")"
            ))

    return results


# =============================================================================
# PLATFORM / WALKWAY CLEARANCES
# =============================================================================

def check_headroom_clearance(
    floor_elevation: float,
    ceiling_elevation: float,
    min_headroom: float = 78.0  # 6'-6"
) -> ClearanceResult:
    """
    Check headroom clearance per OSHA.

    Args:
        floor_elevation: Floor height (inches)
        ceiling_elevation: Ceiling/obstruction height (inches)
        min_headroom: Minimum required headroom (default 78")

    Returns:
        ClearanceResult
    """
    actual = ceiling_elevation - floor_elevation

    if actual < min_headroom:
        severity = SeverityLevel.CRITICAL if actual < 72 else SeverityLevel.WARNING
        return ClearanceResult(
            passes=False,
            clearance_type=ClearanceType.HEADROOM,
            measured=actual,
            required=min_headroom,
            severity=severity,
            location=f"Elev {floor_elevation:.1f}\" to {ceiling_elevation:.1f}\"",
            message=f"Headroom {actual:.1f}\" below min {min_headroom:.1f}\""
        )

    return ClearanceResult(
        passes=True,
        clearance_type=ClearanceType.HEADROOM,
        measured=actual,
        required=min_headroom,
        severity=SeverityLevel.INFO,
        location=f"Elev {floor_elevation:.1f}\" to {ceiling_elevation:.1f}\"",
        message=f"Headroom {actual:.1f}\" OK (min {min_headroom:.1f}\")"
    )


def check_walkway_width(
    width: float,
    walkway_type: str = "general"
) -> ClearanceResult:
    """
    Check walkway width per OSHA 1910.22.

    Args:
        width: Measured width (inches)
        walkway_type: Type of walkway (general, emergency, motor_access)

    Returns:
        ClearanceResult
    """
    min_widths = {
        "general": 28.0,        # Standard walkway
        "emergency": 28.0,      # Emergency egress
        "motor_access": 36.0,   # Motor maintenance
        "ladder_access": 24.0,  # Access to ladder
    }

    min_width = min_widths.get(walkway_type, 28.0)

    if width < min_width:
        return ClearanceResult(
            passes=False,
            clearance_type=ClearanceType.WALKWAY,
            measured=width,
            required=min_width,
            severity=SeverityLevel.CRITICAL,
            location=f"{walkway_type} walkway",
            message=f"Width {width:.1f}\" below min {min_width:.1f}\" for {walkway_type}"
        )

    return ClearanceResult(
        passes=True,
        clearance_type=ClearanceType.WALKWAY,
        measured=width,
        required=min_width,
        severity=SeverityLevel.INFO,
        location=f"{walkway_type} walkway",
        message=f"Width {width:.1f}\" OK (min {min_width:.1f}\")"
    )


# =============================================================================
# PIPING CLEARANCE
# =============================================================================

def check_pipe_clearance(
    pipe_a_od: float,
    pipe_b_od: float,
    center_distance: float,
    is_insulated: bool = False,
    insulation_thickness: float = 0.0
) -> ClearanceResult:
    """
    Check clearance between parallel pipes.

    Args:
        pipe_a_od: Pipe A outside diameter (inches)
        pipe_b_od: Pipe B outside diameter (inches)
        center_distance: Center-to-center distance (inches)
        is_insulated: Whether pipes are insulated
        insulation_thickness: Insulation thickness per side (inches)

    Returns:
        ClearanceResult
    """
    # Calculate actual clearance
    if is_insulated:
        effective_od_a = pipe_a_od + 2 * insulation_thickness
        effective_od_b = pipe_b_od + 2 * insulation_thickness
    else:
        effective_od_a = pipe_a_od
        effective_od_b = pipe_b_od

    actual_clearance = center_distance - (effective_od_a / 2) - (effective_od_b / 2)
    min_clearance = 1.0  # Minimum 1" between bare pipes

    if actual_clearance < 0:
        return ClearanceResult(
            passes=False,
            clearance_type=ClearanceType.PIPING,
            measured=actual_clearance,
            required=min_clearance,
            severity=SeverityLevel.CRITICAL,
            location="Pipe-to-pipe",
            message=f"INTERFERENCE: Pipes overlap by {abs(actual_clearance):.2f}\""
        )

    if actual_clearance < min_clearance:
        return ClearanceResult(
            passes=False,
            clearance_type=ClearanceType.PIPING,
            measured=actual_clearance,
            required=min_clearance,
            severity=SeverityLevel.WARNING,
            location="Pipe-to-pipe",
            message=f"Clearance {actual_clearance:.2f}\" below min {min_clearance:.2f}\""
        )

    return ClearanceResult(
        passes=True,
        clearance_type=ClearanceType.PIPING,
        measured=actual_clearance,
        required=min_clearance,
        severity=SeverityLevel.INFO,
        location="Pipe-to-pipe",
        message=f"Clearance {actual_clearance:.2f}\" OK"
    )


# =============================================================================
# ASSEMBLY ANALYSIS
# =============================================================================

def check_assembly_interference(
    components: list[Component],
    clearance_tolerance: float = 0.0
) -> AssemblyAnalysis:
    """
    Check all components in an assembly for interference.

    Args:
        components: List of Component objects
        clearance_tolerance: Additional clearance to check (0 = touching is OK)

    Returns:
        AssemblyAnalysis with all findings
    """
    analysis = AssemblyAnalysis(
        assembly_name="Assembly",
        total_components=len(components)
    )

    # Check all pairs
    for i in range(len(components)):
        for j in range(i + 1, len(components)):
            comp_a = components[i]
            comp_b = components[j]

            overlaps, dist = check_box_overlap(comp_a.bounds, comp_b.bounds)

            if overlaps:
                analysis.interferences.append(InterferenceResult(
                    has_interference=True,
                    component_a=comp_a.name,
                    component_b=comp_b.name,
                    overlap_distance=dist,
                    severity=SeverityLevel.CRITICAL,
                    location=(
                        (comp_a.bounds.center[0] + comp_b.bounds.center[0]) / 2,
                        (comp_a.bounds.center[1] + comp_b.bounds.center[1]) / 2,
                        (comp_a.bounds.center[2] + comp_b.bounds.center[2]) / 2,
                    ),
                    message=f"Interference between {comp_a.name} and {comp_b.name}: {abs(dist):.3f}\" overlap"
                ))

            elif dist < clearance_tolerance:
                analysis.interferences.append(InterferenceResult(
                    has_interference=False,
                    component_a=comp_a.name,
                    component_b=comp_b.name,
                    overlap_distance=dist,
                    severity=SeverityLevel.WARNING,
                    location=(
                        (comp_a.bounds.center[0] + comp_b.bounds.center[0]) / 2,
                        (comp_a.bounds.center[1] + comp_b.bounds.center[1]) / 2,
                        (comp_a.bounds.center[2] + comp_b.bounds.center[2]) / 2,
                    ),
                    message=f"Low clearance between {comp_a.name} and {comp_b.name}: {dist:.3f}\""
                ))

    return analysis


def check_2d_clearances(
    entities: list[dict],
    min_clearance: float = 1.0
) -> list[ClearanceResult]:
    """
    Check clearances between 2D entities (from DXF/DWG).

    Args:
        entities: List of entities with 'type', 'bounds', 'name'
        min_clearance: Minimum required clearance

    Returns:
        List of ClearanceResult
    """
    results = []

    for i in range(len(entities)):
        for j in range(i + 1, len(entities)):
            ent_a = entities[i]
            ent_b = entities[j]

            box_a = BoundingBox(**ent_a["bounds"])
            box_b = BoundingBox(**ent_b["bounds"])

            overlaps, dist = check_2d_box_overlap(box_a, box_b)

            if overlaps:
                results.append(ClearanceResult(
                    passes=False,
                    clearance_type=ClearanceType.STRUCTURAL,
                    measured=dist,
                    required=min_clearance,
                    severity=SeverityLevel.CRITICAL,
                    location=f"{ent_a.get('name', 'Entity A')} vs {ent_b.get('name', 'Entity B')}",
                    message=f"Overlap detected: {abs(dist):.3f}\""
                ))
            elif dist < min_clearance:
                results.append(ClearanceResult(
                    passes=False,
                    clearance_type=ClearanceType.STRUCTURAL,
                    measured=dist,
                    required=min_clearance,
                    severity=SeverityLevel.WARNING,
                    location=f"{ent_a.get('name', 'Entity A')} vs {ent_b.get('name', 'Entity B')}",
                    message=f"Clearance {dist:.3f}\" below min {min_clearance:.3f}\""
                ))

    return results


# =============================================================================
# NOZZLE CLEARANCE
# =============================================================================

def check_nozzle_clearance(
    nozzle_projection: float,
    flange_od: float,
    adjacent_obstruction_distance: float,
    wrench_clearance: float = 4.0
) -> ClearanceResult:
    """
    Check nozzle has adequate clearance for bolt-up.

    Args:
        nozzle_projection: Distance from vessel to flange face
        flange_od: Flange outside diameter
        adjacent_obstruction_distance: Distance to nearest obstruction
        wrench_clearance: Required wrench swing clearance

    Returns:
        ClearanceResult
    """
    # Check radial clearance for tools
    radial_clearance = adjacent_obstruction_distance - (flange_od / 2)

    if radial_clearance < wrench_clearance:
        return ClearanceResult(
            passes=False,
            clearance_type=ClearanceType.NOZZLE,
            measured=radial_clearance,
            required=wrench_clearance,
            severity=SeverityLevel.WARNING,
            location="Nozzle radial",
            message=f"Radial clearance {radial_clearance:.2f}\" limits wrench access (need {wrench_clearance}\")"
        )

    return ClearanceResult(
        passes=True,
        clearance_type=ClearanceType.NOZZLE,
        measured=radial_clearance,
        required=wrench_clearance,
        severity=SeverityLevel.INFO,
        location="Nozzle radial",
        message=f"Nozzle clearance {radial_clearance:.2f}\" OK for bolt-up"
    )


# =============================================================================
# REPORT GENERATION
# =============================================================================

def generate_interference_report(analysis: AssemblyAnalysis) -> dict:
    """
    Generate a summary report of interference analysis.

    Returns:
        Dictionary with summary and details
    """
    critical_count = len([i for i in analysis.interferences if i.severity == SeverityLevel.CRITICAL])
    warning_count = len([i for i in analysis.interferences if i.severity == SeverityLevel.WARNING])

    critical_clearances = len([c for c in analysis.clearance_violations if c.severity == SeverityLevel.CRITICAL])
    warning_clearances = len([c for c in analysis.clearance_violations if c.severity == SeverityLevel.WARNING])

    return {
        "assembly": analysis.assembly_name,
        "total_components": analysis.total_components,
        "summary": {
            "has_critical_issues": analysis.has_critical_issues,
            "interference_count": len(analysis.interferences),
            "critical_interferences": critical_count,
            "warning_interferences": warning_count,
            "clearance_violations": len(analysis.clearance_violations),
            "critical_clearances": critical_clearances,
            "warning_clearances": warning_clearances,
        },
        "interferences": [
            {
                "components": [i.component_a, i.component_b],
                "overlap": i.overlap_distance,
                "severity": i.severity.value,
                "message": i.message,
            }
            for i in analysis.interferences
        ],
        "clearance_violations": [
            {
                "type": c.clearance_type.value,
                "measured": c.measured,
                "required": c.required,
                "severity": c.severity.value,
                "location": c.location,
                "message": c.message,
            }
            for c in analysis.clearance_violations
        ],
        "status": "FAIL" if analysis.has_critical_issues else "PASS",
    }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "SeverityLevel",
    "ClearanceType",
    # Data classes
    "BoundingBox",
    "Circle2D",
    "Component",
    "InterferenceResult",
    "ClearanceResult",
    "AssemblyAnalysis",
    # Constants
    "MIN_CLEARANCES",
    "FAN_TIP_CLEARANCE_BY_DIA",
    # Box operations
    "check_box_overlap",
    "check_2d_box_overlap",
    # Circle clearances
    "check_circle_clearance",
    "get_fan_tip_clearance_range",
    "check_fan_ring_clearance",
    # Specialized checks
    "check_tube_bundle_path",
    "check_headroom_clearance",
    "check_walkway_width",
    "check_pipe_clearance",
    "check_nozzle_clearance",
    # Assembly analysis
    "check_assembly_interference",
    "check_2d_clearances",
    # Report
    "generate_interference_report",
]
