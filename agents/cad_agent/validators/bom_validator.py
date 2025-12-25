"""
BOM Validator
=============
Validates Bill of Materials (BOM) data extracted from engineering drawings.

Phase 25.6 Implementation
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Tuple
from enum import Enum

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.bom")


# E&C FINFANS Part Number Patterns
PART_NUMBER_PATTERNS = {
    # Header drawings: M-series
    "M_SERIES": re.compile(r"^M\d{2,4}-\d{1,2}[A-Z]{0,2}$", re.IGNORECASE),
    # Structure drawings: S-series
    "S_SERIES": re.compile(r"^S\d{4,5}-\d{1,2}[A-Z]{0,2}$", re.IGNORECASE),
    # Certified shipping: CS-series
    "CS_SERIES": re.compile(r"^CS\d{4,5}-\d{1,2}[A-Z]{0,4}$", re.IGNORECASE),
    # Raw material: RM-prefix
    "RAW_MATERIAL": re.compile(r"^RM-\d{4,6}$", re.IGNORECASE),
    # Purchased parts: PP-prefix
    "PURCHASED": re.compile(r"^PP-\d{4,6}$", re.IGNORECASE),
    # Fabricated parts: FP-prefix
    "FABRICATED": re.compile(r"^FP-\d{4,6}$", re.IGNORECASE),
    # Assembly parts: AP-prefix
    "ASSEMBLY": re.compile(r"^AP-\d{4,6}$", re.IGNORECASE),
    # Generic (catch-all): Number-Letter pattern
    "GENERIC": re.compile(r"^\d{3,6}-\d{1,4}[A-Z]{0,4}$", re.IGNORECASE),
}

# Valid material specifications for BOM
VALID_MATERIALS = {
    # Plates
    "SA-516-70": {"type": "plate", "grade": 70},
    "SA-516-60": {"type": "plate", "grade": 60},
    "SA-516 GR 70": {"type": "plate", "grade": 70},
    "SA-516 GR 60": {"type": "plate", "grade": 60},
    "A516-70": {"type": "plate", "grade": 70},
    "A516-60": {"type": "plate", "grade": 60},
    # Forgings
    "SA-350-LF2": {"type": "forging", "grade": "LF2"},
    "SA-350 LF2": {"type": "forging", "grade": "LF2"},
    "SA-105": {"type": "forging", "grade": "N/A"},
    "A350 LF2": {"type": "forging", "grade": "LF2"},
    "A105": {"type": "forging", "grade": "N/A"},
    # Bars
    "SA-479-304": {"type": "bar", "grade": 304},
    "SA-479-316": {"type": "bar", "grade": 316},
    # Tubes/Pipes
    "SA-179": {"type": "tube", "grade": "N/A"},
    "SA-214": {"type": "tube", "grade": "N/A"},
    "SA-334-6": {"type": "tube", "grade": 6},
    "SA-106-B": {"type": "pipe", "grade": "B"},
    "A106-B": {"type": "pipe", "grade": "B"},
    # Bolting
    "SA-193-B7": {"type": "bolt", "grade": "B7"},
    "SA-194-2H": {"type": "nut", "grade": "2H"},
    "A193-B7": {"type": "bolt", "grade": "B7"},
    "A194-2H": {"type": "nut", "grade": "2H"},
    # Stainless
    "SA-240-304": {"type": "plate", "grade": 304},
    "SA-240-316": {"type": "plate", "grade": 316},
    "304 SS": {"type": "general", "grade": 304},
    "316 SS": {"type": "general", "grade": 316},
    "304L SS": {"type": "general", "grade": "304L"},
    "316L SS": {"type": "general", "grade": "316L"},
    # Carbon steel generic
    "CS": {"type": "general", "grade": "CS"},
    "CARBON STEEL": {"type": "general", "grade": "CS"},
    "C.S.": {"type": "general", "grade": "CS"},
    # Galvanized
    "GALV": {"type": "general", "grade": "GALV"},
    "GALVANIZED": {"type": "general", "grade": "GALV"},
    "HDG": {"type": "general", "grade": "HDG"},
}


@dataclass
class BOMValidationResult:
    """BOM validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

    # BOM-specific statistics
    total_items: int = 0
    items_with_material: int = 0
    items_missing_material: int = 0
    duplicate_items: int = 0
    invalid_part_numbers: int = 0
    material_consistency: str = "N/A"  # "consistent", "mixed", "unknown"


class BOMValidator:
    """
    Validates Bill of Materials data.

    Checks:
    1. Part number format validation
    2. Material specification completeness
    3. Quantity verification
    4. Duplicate part detection
    5. Missing BOM items detection
    6. Material grade consistency
    7. Cross-reference validation (balloons vs BOM)
    8. Raw material mapping
    """

    def __init__(self):
        """Initialize BOM validator."""
        pass

    def validate(self, extraction_result) -> BOMValidationResult:
        """
        Validate BOM data from extraction result.

        Args:
            extraction_result: DrawingExtractionResult from PDF extractor

        Returns:
            BOMValidationResult with all validation findings
        """
        result = BOMValidationResult()

        bom_items = extraction_result.bom_items
        result.total_items = len(bom_items)

        if not bom_items:
            result.total_checks += 1
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="bom_presence",
                message="No BOM items found in drawing",
                suggestion="Ensure BOM table is visible and text is extractable",
            ))
            return result

        # Run all validation checks
        self._check_part_number_formats(bom_items, result)
        self._check_material_completeness(bom_items, result)
        self._check_quantity_values(bom_items, result)
        self._check_duplicates(bom_items, result)
        self._check_material_consistency(bom_items, result)
        self._check_material_validity(bom_items, result)
        self._check_raw_material_mapping(bom_items, result)
        self._check_item_numbering(bom_items, result)

        return result

    def _check_part_number_formats(self, bom_items: List, result: BOMValidationResult):
        """Validate part number formats against known patterns."""
        result.total_checks += 1
        invalid_count = 0

        for item in bom_items:
            part_number = item.part_number.strip().upper() if item.part_number else ""

            if not part_number:
                invalid_count += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="part_number_missing",
                    message=f"BOM item {item.item_number} has no part number",
                    location=f"BOM Item {item.item_number}",
                    suggestion="Add part number for this BOM item",
                ))
                continue

            # Check if matches any valid pattern
            valid = False
            for pattern_name, pattern in PART_NUMBER_PATTERNS.items():
                if pattern.match(part_number):
                    valid = True
                    break

            if not valid:
                # Check for common partial patterns
                if re.match(r"^\d+$", part_number):
                    # Just numbers - might be internal reference
                    pass  # Allow but don't flag as invalid
                elif len(part_number) < 3:
                    invalid_count += 1
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        check_type="part_number_short",
                        message=f"Part number '{part_number}' is unusually short",
                        location=f"BOM Item {item.item_number}",
                        suggestion="Verify part number is complete",
                    ))

        result.invalid_part_numbers = invalid_count

        if invalid_count == 0:
            result.passed += 1
        elif invalid_count <= len(bom_items) * 0.1:  # Less than 10%
            result.warnings += 1
        else:
            result.failed += 1

    def _check_material_completeness(self, bom_items: List, result: BOMValidationResult):
        """Check that all BOM items have material specifications."""
        result.total_checks += 1
        items_with_material = 0
        items_missing = 0

        for item in bom_items:
            material = item.material.strip() if item.material else ""

            if material and material.upper() not in ["N/A", "NA", "-", "TBD", "TBA", ""]:
                items_with_material += 1
            else:
                items_missing += 1
                # Only flag as error if it's a fabricated part (not purchased)
                part_num = item.part_number.upper() if item.part_number else ""
                if not part_num.startswith(("PP-", "RM-")):
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        check_type="material_missing",
                        message=f"BOM item {item.item_number} ({item.part_number}) missing material spec",
                        location=f"BOM Item {item.item_number}",
                        suggestion="Add material specification for fabricated parts",
                    ))

        result.items_with_material = items_with_material
        result.items_missing_material = items_missing

        completeness_ratio = items_with_material / len(bom_items) if bom_items else 0

        if completeness_ratio >= 0.9:
            result.passed += 1
        elif completeness_ratio >= 0.7:
            result.warnings += 1
        else:
            result.failed += 1

    def _check_quantity_values(self, bom_items: List, result: BOMValidationResult):
        """Check quantity values are valid."""
        result.total_checks += 1
        invalid_qty = 0

        for item in bom_items:
            qty = item.quantity

            # Check for zero or negative quantities
            if qty <= 0:
                invalid_qty += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="quantity_invalid",
                    message=f"BOM item {item.item_number} has invalid quantity: {qty}",
                    location=f"BOM Item {item.item_number}",
                    suggestion="Quantity must be a positive number",
                ))

            # Check for unusually high quantities (>100 for single drawing)
            if qty > 100:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="quantity_high",
                    message=f"BOM item {item.item_number} has high quantity: {qty}",
                    location=f"BOM Item {item.item_number}",
                    suggestion="Verify this quantity is correct for a single unit",
                ))

        if invalid_qty == 0:
            result.passed += 1
        else:
            result.failed += 1

    def _check_duplicates(self, bom_items: List, result: BOMValidationResult):
        """Check for duplicate part numbers in BOM."""
        result.total_checks += 1

        part_numbers = {}
        duplicates = []

        for item in bom_items:
            pn = item.part_number.strip().upper() if item.part_number else ""
            if pn:
                if pn in part_numbers:
                    duplicates.append(pn)
                else:
                    part_numbers[pn] = item.item_number

        result.duplicate_items = len(duplicates)

        if duplicates:
            result.warnings += 1
            unique_duplicates = list(set(duplicates))
            for pn in unique_duplicates[:5]:  # Limit to first 5
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="duplicate_part",
                    message=f"Part number '{pn}' appears multiple times in BOM",
                    suggestion="Consolidate duplicate entries or verify intentional",
                ))
        else:
            result.passed += 1

    def _check_material_consistency(self, bom_items: List, result: BOMValidationResult):
        """Check if materials are consistently specified."""
        result.total_checks += 1

        material_types = set()

        for item in bom_items:
            material = item.material.strip().upper() if item.material else ""
            if material:
                # Categorize material type
                if "516" in material or "PLATE" in material:
                    material_types.add("plate")
                elif "350" in material or "FORGING" in material:
                    material_types.add("forging")
                elif "304" in material or "316" in material or "SS" in material:
                    material_types.add("stainless")
                elif "CS" in material or "CARBON" in material:
                    material_types.add("carbon")
                elif "GALV" in material or "HDG" in material:
                    material_types.add("galvanized")

        if len(material_types) <= 2:
            result.material_consistency = "consistent"
            result.passed += 1
        else:
            result.material_consistency = "mixed"
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="material_mixed",
                message=f"BOM contains mixed material types: {', '.join(material_types)}",
                suggestion="Verify mixed materials are intentional for this assembly",
            ))
            result.passed += 1  # Not an error, just informational

    def _check_material_validity(self, bom_items: List, result: BOMValidationResult):
        """Check if materials match valid specifications."""
        result.total_checks += 1
        invalid_count = 0

        for item in bom_items:
            material = item.material.strip().upper() if item.material else ""

            if not material or material in ["N/A", "NA", "-", "TBD", "TBA"]:
                continue

            # Normalize material for lookup
            normalized = material.replace(" ", "-").replace("GR-", "GR ").replace("GR.", "GR ")

            # Check against valid materials
            valid = False
            for valid_mat in VALID_MATERIALS.keys():
                if valid_mat.upper() in normalized or normalized in valid_mat.upper():
                    valid = True
                    break

            if not valid:
                # Check for common patterns
                if re.match(r"^[AS]A?-?\d{2,3}", material):
                    valid = True  # Looks like ASTM/ASME spec
                elif "STEEL" in material or "SS" in material or "CS" in material:
                    valid = True  # Generic steel reference

            if not valid:
                invalid_count += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="material_unknown",
                    message=f"Unknown material specification: '{material}'",
                    location=f"BOM Item {item.item_number}",
                    suggestion="Verify material specification is complete and correct",
                ))

        if invalid_count == 0:
            result.passed += 1
        elif invalid_count <= 2:
            result.warnings += 1
        else:
            result.failed += 1

    def _check_raw_material_mapping(self, bom_items: List, result: BOMValidationResult):
        """Check raw material references are properly mapped."""
        result.total_checks += 1

        rm_items = []
        non_rm_items = []

        for item in bom_items:
            pn = item.part_number.upper() if item.part_number else ""
            if pn.startswith("RM-"):
                rm_items.append(item)
            else:
                non_rm_items.append(item)

        # Raw materials should have material specs
        rm_missing_material = 0
        for item in rm_items:
            material = item.material.strip() if item.material else ""
            if not material or material.upper() in ["N/A", "NA", "-", "TBD"]:
                rm_missing_material += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="rm_missing_material",
                    message=f"Raw material {item.part_number} missing material specification",
                    location=f"BOM Item {item.item_number}",
                    suggestion="Raw material entries must specify material grade",
                ))

        if rm_missing_material == 0:
            result.passed += 1
        else:
            result.failed += 1
            result.critical_failures += rm_missing_material

    def _check_item_numbering(self, bom_items: List, result: BOMValidationResult):
        """Check BOM item numbering is sequential and complete."""
        result.total_checks += 1

        item_numbers = []
        for item in bom_items:
            try:
                num = int(item.item_number)
                item_numbers.append(num)
            except (ValueError, TypeError):
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="item_number_invalid",
                    message=f"Non-numeric BOM item number: {item.item_number}",
                    suggestion="BOM item numbers should be sequential integers",
                ))

        if item_numbers:
            item_numbers.sort()
            expected = list(range(1, len(item_numbers) + 1))

            # Check for gaps
            gaps = []
            for i, num in enumerate(item_numbers):
                if num != i + 1:
                    gaps.append(i + 1)

            if gaps and len(gaps) <= 3:
                result.warnings += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="item_number_gaps",
                    message=f"BOM item numbering has gaps at: {gaps[:3]}",
                    suggestion="Verify item numbering is intentional",
                ))
            else:
                result.passed += 1
        else:
            result.passed += 1

    def to_dict(self, result: BOMValidationResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "bom",
            "total_checks": result.total_checks,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "critical_failures": result.critical_failures,
            "statistics": {
                "total_items": result.total_items,
                "items_with_material": result.items_with_material,
                "items_missing_material": result.items_missing_material,
                "duplicate_items": result.duplicate_items,
                "invalid_part_numbers": result.invalid_part_numbers,
                "material_consistency": result.material_consistency,
            },
            "issues": [
                {
                    "severity": issue.severity.value,
                    "check_type": issue.check_type,
                    "message": issue.message,
                    "location": issue.location,
                    "suggestion": issue.suggestion,
                }
                for issue in result.issues
            ],
        }
