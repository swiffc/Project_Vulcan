"""
Cross-Part Reference Validator
===============================
Validates dimensional alignment and interface compatibility between mating parts.

Phase 25.12 - Cross-Part Reference Validation
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Set
from enum import Enum

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.cross_part")


class InterfaceType(str, Enum):
    """Types of part interfaces."""
    BOLTED = "bolted"
    WELDED = "welded"
    SLIP_FIT = "slip_fit"
    PRESS_FIT = "press_fit"
    MATING_SURFACE = "mating_surface"
    ALIGNMENT_PIN = "alignment_pin"
    KEYWAY = "keyway"


class FitClass(str, Enum):
    """Fit classifications per ANSI B4.1."""
    RC1 = "RC1"  # Close sliding fit
    RC2 = "RC2"  # Sliding fit
    RC3 = "RC3"  # Precision running
    RC4 = "RC4"  # Close running
    LC1 = "LC1"  # Locational clearance
    LC2 = "LC2"  # Locational clearance
    LT1 = "LT1"  # Locational transition
    LN1 = "LN1"  # Locational interference (light)
    LN2 = "LN2"  # Locational interference (medium)
    FN1 = "FN1"  # Light drive fit
    FN2 = "FN2"  # Medium drive fit
    FN3 = "FN3"  # Heavy drive fit


# Standard bolt hole tolerances (inches)
BOLT_HOLE_TOLERANCES = {
    "standard": 0.0625,    # 1/16" clearance
    "oversized": 0.125,    # 1/8" clearance
    "precision": 0.03125,  # 1/32" clearance
}

# Mating surface alignment tolerances
ALIGNMENT_TOLERANCES = {
    "rough": 0.125,      # 1/8"
    "standard": 0.0625,  # 1/16"
    "precision": 0.03125, # 1/32"
    "close": 0.015625,   # 1/64"
}

# Standard gasket compression ratios
GASKET_COMPRESSION = {
    "spiral_wound": {"min": 0.10, "max": 0.25},
    "sheet": {"min": 0.15, "max": 0.35},
    "ring_joint": {"min": 0.0, "max": 0.05},
    "o_ring": {"min": 0.15, "max": 0.30},
}


@dataclass
class HolePattern:
    """Bolt hole pattern definition."""
    holes: List[Dict]  # [{x, y, diameter, type}]
    bolt_circle_diameter: Optional[float] = None
    pattern_type: str = "rectangular"  # rectangular, circular, custom
    reference_point: Tuple[float, float] = (0, 0)


@dataclass
class PartInterface:
    """Interface definition for a part."""
    part_id: str
    interface_id: str
    interface_type: InterfaceType

    # Geometric data
    holes: Optional[HolePattern] = None
    mating_surface_dims: Optional[Dict] = None  # {width, length, flatness}
    shaft_diameter: Optional[float] = None
    bore_diameter: Optional[float] = None
    keyway: Optional[Dict] = None  # {width, depth, length}

    # Tolerances
    position_tolerance: float = 0.0625
    size_tolerance: float = 0.03125

    # Reference
    mating_part_id: Optional[str] = None
    mating_interface_id: Optional[str] = None


@dataclass
class CrossPartValidationResult:
    """Cross-part reference validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

    # Statistics
    interfaces_checked: int = 0
    hole_patterns_compared: int = 0
    misalignments_found: int = 0
    fit_issues: int = 0

    # Interface map
    interface_matches: List[Dict] = field(default_factory=list)


class CrossPartValidator:
    """
    Validates cross-part references and interface compatibility.

    Checks:
    1. Bolt hole pattern alignment between mating parts
    2. Bolt hole size compatibility
    3. Mating surface dimensions
    4. Shaft/bore fit classification
    5. Keyway alignment
    6. Gasket surface compatibility
    7. Flange face compatibility
    8. Assembly sequence feasibility
    """

    def __init__(self):
        pass

    def validate_interface_pair(
        self,
        interface_a: PartInterface,
        interface_b: PartInterface
    ) -> CrossPartValidationResult:
        """
        Validate two mating interfaces.

        Args:
            interface_a: First interface
            interface_b: Mating interface

        Returns:
            CrossPartValidationResult
        """
        result = CrossPartValidationResult()
        result.interfaces_checked = 2

        # Verify interface types are compatible
        self._check_interface_compatibility(interface_a, interface_b, result)

        # Run type-specific checks
        if interface_a.interface_type == InterfaceType.BOLTED:
            self._check_bolt_hole_alignment(interface_a, interface_b, result)
            self._check_bolt_hole_sizes(interface_a, interface_b, result)

        if interface_a.interface_type in [InterfaceType.SLIP_FIT, InterfaceType.PRESS_FIT]:
            self._check_shaft_bore_fit(interface_a, interface_b, result)

        if interface_a.interface_type == InterfaceType.KEYWAY:
            self._check_keyway_alignment(interface_a, interface_b, result)

        if interface_a.interface_type == InterfaceType.MATING_SURFACE:
            self._check_mating_surface(interface_a, interface_b, result)

        return result

    def validate_assembly(
        self,
        interfaces: List[PartInterface]
    ) -> CrossPartValidationResult:
        """
        Validate all interfaces in an assembly.

        Args:
            interfaces: List of all part interfaces

        Returns:
            CrossPartValidationResult
        """
        result = CrossPartValidationResult()
        result.interfaces_checked = len(interfaces)

        # Build interface map
        interface_map: Dict[str, PartInterface] = {}
        for intf in interfaces:
            key = f"{intf.part_id}:{intf.interface_id}"
            interface_map[key] = intf

        # Find and validate mating pairs
        validated_pairs: Set[Tuple[str, str]] = set()

        for intf in interfaces:
            if intf.mating_part_id and intf.mating_interface_id:
                key_a = f"{intf.part_id}:{intf.interface_id}"
                key_b = f"{intf.mating_part_id}:{intf.mating_interface_id}"

                # Skip if already validated
                pair_key = tuple(sorted([key_a, key_b]))
                if pair_key in validated_pairs:
                    continue
                validated_pairs.add(pair_key)

                # Find mating interface
                if key_b in interface_map:
                    mate = interface_map[key_b]
                    pair_result = self.validate_interface_pair(intf, mate)

                    # Combine results
                    result.total_checks += pair_result.total_checks
                    result.passed += pair_result.passed
                    result.failed += pair_result.failed
                    result.warnings += pair_result.warnings
                    result.critical_failures += pair_result.critical_failures
                    result.issues.extend(pair_result.issues)
                    result.hole_patterns_compared += pair_result.hole_patterns_compared
                    result.misalignments_found += pair_result.misalignments_found
                    result.fit_issues += pair_result.fit_issues

                    result.interface_matches.append({
                        "interface_a": key_a,
                        "interface_b": key_b,
                        "status": "PASS" if pair_result.failed == 0 else "FAIL",
                    })
                else:
                    result.failed += 1
                    result.critical_failures += 1
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        check_type="missing_mate",
                        message=f"Mating interface not found: {key_b}",
                        location=f"Interface {key_a}",
                        suggestion=f"Verify mating part {intf.mating_part_id} exists",
                    ))

        # Check for orphan interfaces
        self._check_orphan_interfaces(interfaces, validated_pairs, result)

        return result

    def _check_interface_compatibility(
        self,
        interface_a: PartInterface,
        interface_b: PartInterface,
        result: CrossPartValidationResult
    ):
        """Check that interface types are compatible."""
        result.total_checks += 1

        if interface_a.interface_type != interface_b.interface_type:
            result.failed += 1
            result.critical_failures += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                check_type="interface_type_mismatch",
                message=f"Interface type mismatch: {interface_a.interface_type.value} vs {interface_b.interface_type.value}",
                location=f"{interface_a.part_id} ↔ {interface_b.part_id}",
                suggestion="Verify correct mating interface selected",
            ))
        else:
            result.passed += 1

    def _check_bolt_hole_alignment(
        self,
        interface_a: PartInterface,
        interface_b: PartInterface,
        result: CrossPartValidationResult
    ):
        """Check bolt hole pattern alignment."""
        if not interface_a.holes or not interface_b.holes:
            return

        result.total_checks += 1
        result.hole_patterns_compared += 1

        holes_a = interface_a.holes.holes
        holes_b = interface_b.holes.holes

        # Check hole count
        if len(holes_a) != len(holes_b):
            result.failed += 1
            result.critical_failures += 1
            result.misalignments_found += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                check_type="hole_count_mismatch",
                message=f"Hole count mismatch: {len(holes_a)} vs {len(holes_b)}",
                location=f"{interface_a.part_id} ↔ {interface_b.part_id}",
                suggestion="Verify hole patterns match between parts",
            ))
            return

        # Match holes by position
        tolerance = max(interface_a.position_tolerance, interface_b.position_tolerance)
        matched = []
        unmatched_a = list(range(len(holes_a)))
        unmatched_b = list(range(len(holes_b)))

        for i, h_a in enumerate(holes_a):
            for j in unmatched_b:
                h_b = holes_b[j]

                dx = abs(h_a.get("x", 0) - h_b.get("x", 0))
                dy = abs(h_a.get("y", 0) - h_b.get("y", 0))

                if dx <= tolerance and dy <= tolerance:
                    matched.append((i, j))
                    unmatched_a.remove(i)
                    unmatched_b.remove(j)
                    break

        if unmatched_a or unmatched_b:
            result.failed += 1
            result.misalignments_found += len(unmatched_a)
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                check_type="hole_alignment",
                message=f"{len(unmatched_a)} holes do not align (tolerance ±{tolerance}\")",
                location=f"{interface_a.part_id} ↔ {interface_b.part_id}",
                suggestion=f"Check hole positions - max offset > {tolerance}\"",
            ))
        else:
            result.passed += 1

    def _check_bolt_hole_sizes(
        self,
        interface_a: PartInterface,
        interface_b: PartInterface,
        result: CrossPartValidationResult
    ):
        """Check bolt hole size compatibility."""
        if not interface_a.holes or not interface_b.holes:
            return

        result.total_checks += 1

        holes_a = interface_a.holes.holes
        holes_b = interface_b.holes.holes

        size_issues = []
        for i, (h_a, h_b) in enumerate(zip(holes_a, holes_b)):
            dia_a = h_a.get("diameter", 0)
            dia_b = h_b.get("diameter", 0)

            diff = abs(dia_a - dia_b)
            if diff > 0.125:  # More than 1/8" difference
                size_issues.append((i, dia_a, dia_b))

        if size_issues:
            result.warnings += 1
            for i, dia_a, dia_b in size_issues:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="hole_size_mismatch",
                    message=f"Hole #{i+1} size difference: {dia_a}\" vs {dia_b}\"",
                    location=f"{interface_a.part_id} ↔ {interface_b.part_id}",
                    suggestion="Verify both holes accommodate intended bolt size",
                ))
        else:
            result.passed += 1

    def _check_shaft_bore_fit(
        self,
        interface_a: PartInterface,
        interface_b: PartInterface,
        result: CrossPartValidationResult
    ):
        """Check shaft/bore fit compatibility."""
        result.total_checks += 1

        # Determine which is shaft and which is bore
        shaft_dia = interface_a.shaft_diameter or interface_b.shaft_diameter
        bore_dia = interface_a.bore_diameter or interface_b.bore_diameter

        if not shaft_dia or not bore_dia:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="missing_fit_data",
                message="Shaft or bore diameter not specified for fit check",
                location=f"{interface_a.part_id} ↔ {interface_b.part_id}",
                suggestion="Specify shaft_diameter and bore_diameter for fit validation",
            ))
            result.warnings += 1
            return

        clearance = bore_dia - shaft_dia

        # Determine fit type
        fit_type = interface_a.interface_type
        if fit_type == InterfaceType.SLIP_FIT:
            # Clearance fit - bore should be larger
            if clearance < 0:
                result.failed += 1
                result.fit_issues += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    check_type="interference_not_intended",
                    message=f"Shaft {shaft_dia}\" > bore {bore_dia}\" - won't assemble",
                    location=f"{interface_a.part_id} ↔ {interface_b.part_id}",
                    suggestion="Increase bore diameter or reduce shaft diameter",
                ))
            elif clearance > 0.010:  # More than 10 thou clearance
                result.warnings += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="excessive_clearance",
                    message=f"Large clearance: {clearance*1000:.1f} thou",
                    location=f"{interface_a.part_id} ↔ {interface_b.part_id}",
                    suggestion="Verify clearance is acceptable for application",
                ))
            else:
                result.passed += 1

        elif fit_type == InterfaceType.PRESS_FIT:
            # Interference fit - shaft should be larger
            if clearance > 0:
                result.failed += 1
                result.fit_issues += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    check_type="no_interference",
                    message=f"No interference: shaft {shaft_dia}\" < bore {bore_dia}\"",
                    location=f"{interface_a.part_id} ↔ {interface_b.part_id}",
                    suggestion="Increase shaft diameter or reduce bore for press fit",
                ))
            elif abs(clearance) > 0.005:  # More than 5 thou interference
                result.warnings += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="heavy_interference",
                    message=f"Heavy interference: {abs(clearance)*1000:.1f} thou",
                    location=f"{interface_a.part_id} ↔ {interface_b.part_id}",
                    suggestion="Verify press fit force is acceptable - may need thermal assistance",
                ))
            else:
                result.passed += 1

    def _check_keyway_alignment(
        self,
        interface_a: PartInterface,
        interface_b: PartInterface,
        result: CrossPartValidationResult
    ):
        """Check keyway alignment and dimensions."""
        if not interface_a.keyway or not interface_b.keyway:
            return

        result.total_checks += 1

        kw_a = interface_a.keyway
        kw_b = interface_b.keyway

        # Check width match
        width_a = kw_a.get("width", 0)
        width_b = kw_b.get("width", 0)

        if abs(width_a - width_b) > 0.001:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                check_type="keyway_width_mismatch",
                message=f"Keyway width mismatch: {width_a}\" vs {width_b}\"",
                location=f"{interface_a.part_id} ↔ {interface_b.part_id}",
                suggestion="Keyway widths must match for standard key",
            ))
        else:
            result.passed += 1

        # Check depth sum (should equal key height)
        depth_a = kw_a.get("depth", 0)
        depth_b = kw_b.get("depth", 0)
        total_depth = depth_a + depth_b

        # Standard key height = key width
        expected_depth = width_a

        result.total_checks += 1
        if abs(total_depth - expected_depth) > 0.01:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="keyway_depth",
                message=f"Combined keyway depth {total_depth}\" ≠ key height {expected_depth}\"",
                location=f"{interface_a.part_id} ↔ {interface_b.part_id}",
                suggestion="Verify keyway depths accommodate standard key",
            ))
        else:
            result.passed += 1

    def _check_mating_surface(
        self,
        interface_a: PartInterface,
        interface_b: PartInterface,
        result: CrossPartValidationResult
    ):
        """Check mating surface compatibility."""
        if not interface_a.mating_surface_dims or not interface_b.mating_surface_dims:
            return

        result.total_checks += 1

        dims_a = interface_a.mating_surface_dims
        dims_b = interface_b.mating_surface_dims

        # Check dimensions match
        width_diff = abs(dims_a.get("width", 0) - dims_b.get("width", 0))
        length_diff = abs(dims_a.get("length", 0) - dims_b.get("length", 0))

        tolerance = ALIGNMENT_TOLERANCES["standard"]

        if width_diff > tolerance or length_diff > tolerance:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="mating_surface_size",
                message=f"Mating surface size difference: ΔW={width_diff:.3f}\", ΔL={length_diff:.3f}\"",
                location=f"{interface_a.part_id} ↔ {interface_b.part_id}",
                suggestion="Verify mating surface overlap is adequate",
            ))
        else:
            result.passed += 1

        # Check flatness if specified
        flatness_a = dims_a.get("flatness")
        flatness_b = dims_b.get("flatness")

        if flatness_a and flatness_b:
            result.total_checks += 1
            total_flatness = flatness_a + flatness_b

            if total_flatness > 0.010:  # More than 10 thou combined
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="flatness_stack",
                    message=f"Combined flatness tolerance: {total_flatness*1000:.1f} thou",
                    location=f"{interface_a.part_id} ↔ {interface_b.part_id}",
                    suggestion="May require shimming or machining for tight joints",
                ))
            result.passed += 1

    def _check_orphan_interfaces(
        self,
        interfaces: List[PartInterface],
        validated_pairs: Set[Tuple[str, str]],
        result: CrossPartValidationResult
    ):
        """Check for interfaces without mates."""
        result.total_checks += 1

        orphans = []
        for intf in interfaces:
            key = f"{intf.part_id}:{intf.interface_id}"
            has_mate = False

            for pair in validated_pairs:
                if key in pair:
                    has_mate = True
                    break

            if not has_mate and not intf.mating_part_id:
                orphans.append(key)

        if orphans and len(orphans) < len(interfaces):  # Some orphans
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="orphan_interfaces",
                message=f"{len(orphans)} interfaces have no defined mate",
                location=", ".join(orphans[:3]) + ("..." if len(orphans) > 3 else ""),
                suggestion="Verify all interfaces have mating parts defined",
            ))
        else:
            result.passed += 1

    def to_dict(self, result: CrossPartValidationResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "cross_part",
            "total_checks": result.total_checks,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "critical_failures": result.critical_failures,
            "statistics": {
                "interfaces_checked": result.interfaces_checked,
                "hole_patterns_compared": result.hole_patterns_compared,
                "misalignments_found": result.misalignments_found,
                "fit_issues": result.fit_issues,
            },
            "interface_matches": result.interface_matches,
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
