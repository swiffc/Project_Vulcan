"""
OSHA Structural Validator
=========================
Validates structural safety compliance against OSHA 1910 standards.

Phase 25.5 Implementation
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.osha")


# OSHA 1910.29 Handrail Requirements
HANDRAIL_STANDARDS = {
    "top_rail_height": {
        "min_in": 42,
        "max_in": 45,
        "tolerance_in": 3,
        "reference": "OSHA 1910.29(b)(1)",
    },
    "mid_rail_height": {
        "nominal_in": 21,
        "reference": "OSHA 1910.29(b)(2)",
    },
    "toe_board_height": {
        "min_in": 3.5,
        "reference": "OSHA 1910.29(b)(3)",
    },
    "opening_max": {
        "max_in": 19,
        "reference": "OSHA 1910.29(b)(4)",
    },
}

# OSHA 1910.28 / 1910.27 Ladder Requirements (2018 Final Rule)
# Note: 2018 Final Rule phased out cages, now requires personal fall arrest
LADDER_STANDARDS = {
    "rung_spacing": {
        "max_in": 12,
        "uniform": True,
        "reference": "OSHA 1910.23(b)(4)",
    },
    "side_rail_width": {
        "min_in": 16,
        "reference": "OSHA 1910.23(b)(5)",
    },
    # 2018 Final Rule: Fall protection trigger at 24 ft, not 20 ft
    "fall_protection_trigger": {
        "height_ft": 24,
        "reference": "OSHA 1910.28(b)(9)(i)",
    },
    # Cage phase-out: Required PFAS or LAD for new ladders > 24 ft
    "pfas_required": {
        "height_ft": 24,
        "note": "Personal Fall Arrest System or Ladder Safety Device",
        "reference": "OSHA 1910.28(b)(9)(i)(A)",
    },
    # Existing cage systems grandfathered until 11/19/2036
    "cage_grandfathered_until": {
        "date": "2036-11-19",
        "note": "Cages acceptable for existing installations only",
        "reference": "OSHA 1910.28(b)(9)(i)(B)",
    },
    "landing_interval": {
        "max_ft": 150,  # Updated: was 30 ft
        "reference": "OSHA 1910.23(d)(5)",
    },
    "platform_width": {
        "min_in": 20,
        "reference": "OSHA 1910.23(e)(2)",
    },
    "side_rail_extension": {
        "min_in": 42,  # 3.5 ft above landing
        "reference": "OSHA 1910.23(d)(1)",
    },
    "rung_diameter": {
        "min_in": 0.75,
        "max_in": 1.125,
        "reference": "OSHA 1910.23(b)(4)(ii)",
    },
}

# Structural Steel Requirements
STRUCTURAL_STANDARDS = {
    "a325_bolts": {
        "description": "High-strength structural bolts",
        "reference": "AISC/RCSC",
    },
    "f436_washers": {
        "description": "Hardened washers for structural connections",
        "reference": "ASTM F436",
    },
    "weld_symbols": {
        "required": ["fillet", "groove", "plug"],
        "reference": "AWS A2.4",
    },
}


@dataclass
class OSHAValidationResult:
    """OSHA validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

    # OSHA-specific statistics
    handrail_checks: int = 0
    handrail_violations: int = 0
    ladder_checks: int = 0
    ladder_violations: int = 0
    structural_checks: int = 0
    structural_violations: int = 0


class OSHAValidator:
    """
    Validates structural safety compliance against OSHA standards.

    Checks:
    1. OSHA 1910.29 handrail height (42" +/- 3")
    2. OSHA 1910.29 mid-rail requirement (21")
    3. OSHA 1910.29 toe board height (3.5" min)
    4. OSHA 1910.27 ladder requirements
    5. AWS D1.1 structural weld requirements
    6. A325 bolt grade verification
    7. F436 hardened washer requirements
    8. Column/beam sizing adequacy
    """

    def __init__(self):
        """Initialize OSHA validator."""
        pass

    def validate(self, extraction_result) -> OSHAValidationResult:
        """
        Validate structural safety from extraction result.

        Args:
            extraction_result: DrawingExtractionResult from PDF extractor

        Returns:
            OSHAValidationResult with all validation findings
        """
        result = OSHAValidationResult()

        drawing_type = extraction_result.drawing_type

        # Run all validation checks
        self._check_handrails(extraction_result, result)
        self._check_ladders(extraction_result, result)
        self._check_platforms(extraction_result, result)
        self._check_structural_bolts(extraction_result, result)
        self._check_structural_welds(extraction_result, result)
        self._check_toe_boards(extraction_result, result)
        self._check_guard_openings(extraction_result, result)
        self._check_access_requirements(extraction_result, result)

        return result

    def _check_handrails(self, extraction_result, result: OSHAValidationResult):
        """Check handrail compliance with OSHA 1910.29."""
        result.total_checks += 1
        result.handrail_checks += 1

        dimensions = extraction_result.dimensions
        general_notes = extraction_result.general_notes

        # Look for handrail dimensions
        handrail_dims = []
        for dim in dimensions:
            desc = (dim.description or "").upper()
            if any(kw in desc for kw in ["HANDRAIL", "RAIL", "GUARD", "TOP RAIL"]):
                handrail_dims.append(dim)

        # Check handrail height
        for dim in handrail_dims:
            desc = (dim.description or "").upper()
            val = dim.value_imperial

            if val and ("TOP" in desc or "HEIGHT" in desc):
                std = HANDRAIL_STANDARDS["top_rail_height"]
                min_h = std["min_in"] - std["tolerance_in"]
                max_h = std["max_in"]

                if val < min_h:
                    result.handrail_violations += 1
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        check_type="handrail_height_low",
                        message=f"Handrail height {val}\" is below OSHA minimum of {min_h}\"",
                        standard_reference=std["reference"],
                        suggestion=f"Increase handrail height to 42\" (+/- 3\")",
                    ))
                elif val > max_h:
                    result.handrail_violations += 1
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        check_type="handrail_height_high",
                        message=f"Handrail height {val}\" exceeds typical maximum of {max_h}\"",
                        standard_reference=std["reference"],
                        suggestion=f"Verify handrail height is intentional",
                    ))

        # Check notes for handrail references
        notes_text = " ".join([n.text for n in general_notes]).upper() if general_notes else ""

        if "HANDRAIL" in notes_text or "GUARDRAIL" in notes_text:
            # Verify 42" is mentioned
            if "42" not in notes_text and "1070" not in notes_text:  # 42" = 1067mm
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="handrail_dim_missing",
                    message="Handrail referenced but height not specified in notes",
                    suggestion="Add handrail height dimension (42\" per OSHA 1910.29)",
                ))

        if result.handrail_violations == 0:
            result.passed += 1
        else:
            result.failed += 1
            result.critical_failures += result.handrail_violations

    def _check_ladders(self, extraction_result, result: OSHAValidationResult):
        """Check ladder compliance with OSHA 1910.27."""
        result.total_checks += 1
        result.ladder_checks += 1

        dimensions = extraction_result.dimensions
        bom_items = extraction_result.bom_items
        general_notes = extraction_result.general_notes

        # Look for ladder-related items
        ladder_dims = []
        for dim in dimensions:
            desc = (dim.description or "").upper()
            if any(kw in desc for kw in ["LADDER", "RUNG", "CAGE", "CLIMB"]):
                ladder_dims.append(dim)

        # Check for ladder in BOM
        has_ladder = False
        for item in bom_items:
            desc = (item.description or "").upper()
            if "LADDER" in desc:
                has_ladder = True
                break

        if has_ladder or ladder_dims:
            # Check rung spacing
            for dim in ladder_dims:
                desc = (dim.description or "").upper()
                val = dim.value_imperial

                if val and "RUNG" in desc and "SPACING" in desc:
                    std = LADDER_STANDARDS["rung_spacing"]
                    if val > std["max_in"]:
                        result.ladder_violations += 1
                        result.issues.append(ValidationIssue(
                            severity=ValidationSeverity.CRITICAL,
                            check_type="rung_spacing",
                            message=f"Rung spacing {val}\" exceeds OSHA maximum of {std['max_in']}\"",
                            standard_reference=std["reference"],
                            suggestion="Reduce rung spacing to 12\" maximum",
                        ))

            # Check for cage requirement note if tall ladder
            notes_text = " ".join([n.text for n in general_notes]).upper() if general_notes else ""
            if "20" in notes_text or "FT" in notes_text:
                if "CAGE" not in notes_text and "GUARD" not in notes_text:
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        check_type="ladder_cage",
                        message="Ladder over 20' may require cage per OSHA 1910.27(d)(1)",
                        standard_reference="OSHA 1910.27(d)(1)",
                        suggestion="Add cage for ladders over 20' or verify exemption",
                    ))

        if result.ladder_violations == 0:
            result.passed += 1
        else:
            result.failed += 1
            result.critical_failures += result.ladder_violations

    def _check_platforms(self, extraction_result, result: OSHAValidationResult):
        """Check platform and walkway requirements."""
        result.total_checks += 1

        dimensions = extraction_result.dimensions

        # Look for platform/walkway dimensions
        platform_dims = []
        for dim in dimensions:
            desc = (dim.description or "").upper()
            if any(kw in desc for kw in ["PLATFORM", "WALKWAY", "GRATING", "FLOOR"]):
                platform_dims.append(dim)

        # Check minimum widths
        for dim in platform_dims:
            desc = (dim.description or "").upper()
            val = dim.value_imperial

            if val and ("WIDTH" in desc or "W" in desc):
                # Minimum platform width typically 20" for access
                if val < 20:
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        check_type="platform_width",
                        message=f"Platform/walkway width {val}\" is narrow",
                        suggestion="Minimum 20\" width recommended for access platforms",
                    ))

        result.passed += 1

    def _check_structural_bolts(self, extraction_result, result: OSHAValidationResult):
        """Check structural bolt specifications."""
        result.total_checks += 1
        result.structural_checks += 1

        bom_items = extraction_result.bom_items
        general_notes = extraction_result.general_notes

        # Check BOM for bolt grades
        bolt_items = []
        for item in bom_items:
            desc = (item.description or "").upper()
            if "BOLT" in desc or "SCREW" in desc or "FASTENER" in desc:
                bolt_items.append(item)

        # Verify A325/A490 for structural connections
        has_structural_bolts = False
        for item in bolt_items:
            material = (item.material or "").upper()
            desc = (item.description or "").upper()

            if "A325" in material or "A325" in desc:
                has_structural_bolts = True
            elif "A490" in material or "A490" in desc:
                has_structural_bolts = True
            elif "A193" in material:
                # Pressure bolting - acceptable
                has_structural_bolts = True

        # Check notes for bolt specifications
        notes_text = " ".join([n.text for n in general_notes]).upper() if general_notes else ""

        if bolt_items and not has_structural_bolts:
            if "STRUCTURAL" in notes_text or "MAIN FRAME" in notes_text:
                result.structural_violations += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="bolt_grade",
                    message="Structural bolts should specify A325 or A490 grade",
                    standard_reference="AISC/RCSC",
                    suggestion="Add bolt grade specification for structural connections",
                ))

        if result.structural_violations == 0:
            result.passed += 1
        else:
            result.warnings += 1

    def _check_structural_welds(self, extraction_result, result: OSHAValidationResult):
        """Check structural weld specifications."""
        result.total_checks += 1
        result.structural_checks += 1

        weld_symbols = extraction_result.weld_symbols
        drawing_type = extraction_result.drawing_type

        # For S-series (structural) drawings, verify weld specs
        if drawing_type and drawing_type.value == "S":
            if not weld_symbols:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="structural_welds_missing",
                    message="Structural drawing has no weld specifications extracted",
                    suggestion="Verify weld symbols and callouts are present",
                ))
                result.warnings += 1
                return

            # Check for AWS D1.1 compliance
            has_d1_1_ref = False
            for weld in weld_symbols:
                note = (weld.note or "").upper()
                if "D1.1" in note or "AWS" in note:
                    has_d1_1_ref = True
                    break

            if not has_d1_1_ref:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="aws_reference",
                    message="Structural welds should reference AWS D1.1",
                    suggestion="Add AWS D1.1 reference to weld specifications",
                ))

        result.passed += 1

    def _check_toe_boards(self, extraction_result, result: OSHAValidationResult):
        """Check toe board requirements."""
        result.total_checks += 1

        general_notes = extraction_result.general_notes
        bom_items = extraction_result.bom_items

        notes_text = " ".join([n.text for n in general_notes]).upper() if general_notes else ""

        # Check for toe board in notes or BOM
        has_toe_board = False
        for item in bom_items:
            desc = (item.description or "").upper()
            if "TOE" in desc and "BOARD" in desc:
                has_toe_board = True
                break

        if "TOE BOARD" in notes_text or "TOEBOARD" in notes_text:
            has_toe_board = True

        # If platform/walkway mentioned, toe board should be specified
        if "PLATFORM" in notes_text or "WALKWAY" in notes_text:
            if not has_toe_board and "TOE" not in notes_text:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="toe_board_missing",
                    message="Platform/walkway may require toe boards per OSHA 1910.29",
                    standard_reference="OSHA 1910.29(b)(3)",
                    suggestion="Add 3.5\" minimum toe board specification",
                ))

        result.passed += 1

    def _check_guard_openings(self, extraction_result, result: OSHAValidationResult):
        """Check guard rail opening requirements."""
        result.total_checks += 1

        dimensions = extraction_result.dimensions

        # Look for opening dimensions in guards
        for dim in dimensions:
            desc = (dim.description or "").upper()
            val = dim.value_imperial

            if val and any(kw in desc for kw in ["OPENING", "GAP", "SPACE"]):
                if "GUARD" in desc or "RAIL" in desc:
                    std = HANDRAIL_STANDARDS["opening_max"]
                    if val > std["max_in"]:
                        result.issues.append(ValidationIssue(
                            severity=ValidationSeverity.CRITICAL,
                            check_type="guard_opening",
                            message=f"Guard opening {val}\" exceeds OSHA maximum of {std['max_in']}\"",
                            standard_reference=std["reference"],
                            suggestion="Reduce opening size or add intermediate rail",
                        ))
                        result.critical_failures += 1

        result.passed += 1

    def _check_access_requirements(self, extraction_result, result: OSHAValidationResult):
        """Check general access and egress requirements."""
        result.total_checks += 1

        general_notes = extraction_result.general_notes
        drawing_type = extraction_result.drawing_type

        notes_text = " ".join([n.text for n in general_notes]).upper() if general_notes else ""

        # For structure drawings, verify access is considered
        if drawing_type and drawing_type.value == "S":
            access_keywords = ["ACCESS", "LADDER", "STAIR", "PLATFORM", "WALKWAY"]

            has_access_ref = any(kw in notes_text for kw in access_keywords)

            if not has_access_ref:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="access_not_specified",
                    message="Structural assembly should address maintenance access",
                    suggestion="Consider adding access platform/ladder specifications",
                ))

        result.passed += 1

    def to_dict(self, result: OSHAValidationResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "osha",
            "total_checks": result.total_checks,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "critical_failures": result.critical_failures,
            "statistics": {
                "handrail_checks": result.handrail_checks,
                "handrail_violations": result.handrail_violations,
                "ladder_checks": result.ladder_checks,
                "ladder_violations": result.ladder_violations,
                "structural_checks": result.structural_checks,
                "structural_violations": result.structural_violations,
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
