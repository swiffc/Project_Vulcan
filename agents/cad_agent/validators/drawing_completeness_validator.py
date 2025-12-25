"""
Drawing Completeness Validator
==============================
Validates that engineering drawings have all required elements.

Phase 25.8 Implementation
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
from enum import Enum

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.completeness")


# Required title block fields
REQUIRED_TITLE_BLOCK_FIELDS = {
    "part_number": {"required": True, "severity": "critical"},
    "revision": {"required": True, "severity": "critical"},
    "title": {"required": True, "severity": "error"},
    "customer": {"required": False, "severity": "warning"},
    "project_number": {"required": False, "severity": "warning"},
    "date": {"required": True, "severity": "error"},
    "drawn_by": {"required": True, "severity": "error"},
    "checked_by": {"required": False, "severity": "warning"},
    "approved_by": {"required": False, "severity": "warning"},
    "scale": {"required": True, "severity": "warning"},
}

# Required notes by drawing type
REQUIRED_NOTES_BY_TYPE = {
    "M": [  # Header drawings
        "material",
        "weld",
        "surface finish",
        "heat treatment",
    ],
    "S": [  # Structure drawings
        "material",
        "weld",
        "surface finish",
        "paint",
    ],
    "CS": [  # Shipping/Lifting drawings
        "weight",
        "lifting",
        "rigging",
        "shipping",
    ],
}

# Standard view requirements
VIEW_REQUIREMENTS = {
    "section": {
        "description": "Section views for internal features",
        "keywords": ["SECTION", "SEC", "A-A", "B-B", "C-C"],
    },
    "detail": {
        "description": "Detail views for critical features",
        "keywords": ["DETAIL", "DET", "DTL", "VIEW"],
    },
    "isometric": {
        "description": "Isometric/3D view for assembly clarity",
        "keywords": ["ISOMETRIC", "ISO", "3D", "PICTORIAL"],
    },
}


@dataclass
class CompletenessValidationResult:
    """Drawing completeness validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

    # Completeness-specific statistics
    title_block_complete: bool = False
    title_block_fields_present: int = 0
    title_block_fields_missing: int = 0
    revision_history_present: bool = False
    revision_entries: int = 0
    general_notes_present: bool = False
    general_notes_count: int = 0
    bom_present: bool = False
    bom_items: int = 0
    weld_details_present: bool = False
    section_views_present: bool = False
    detail_views_present: bool = False


class DrawingCompletenessValidator:
    """
    Validates drawing completeness.

    Checks:
    1. Title block completeness (all fields populated)
    2. Revision history completeness
    3. General notes presence and completeness
    4. Shop notes presence
    5. Weld detail callouts present
    6. Section views for complex areas
    7. Detail views for critical features
    8. Scale verification per view
    9. Third angle projection symbol
    10. Copyright/proprietary notice
    """

    def __init__(self):
        """Initialize completeness validator."""
        pass

    def validate(self, extraction_result) -> CompletenessValidationResult:
        """
        Validate drawing completeness from extraction result.

        Args:
            extraction_result: DrawingExtractionResult from PDF extractor

        Returns:
            CompletenessValidationResult with all validation findings
        """
        result = CompletenessValidationResult()

        # Run all completeness checks
        self._check_title_block(extraction_result, result)
        self._check_revision_history(extraction_result, result)
        self._check_general_notes(extraction_result, result)
        self._check_shop_notes(extraction_result, result)
        self._check_weld_details(extraction_result, result)
        self._check_section_views(extraction_result, result)
        self._check_detail_views(extraction_result, result)
        self._check_scale(extraction_result, result)
        self._check_projection_symbol(extraction_result, result)
        self._check_proprietary_notice(extraction_result, result)

        return result

    def _check_title_block(self, extraction_result, result: CompletenessValidationResult):
        """Check title block completeness."""
        result.total_checks += 1

        title_block = extraction_result.title_block
        fields_present = 0
        fields_missing = 0

        # Check each required field
        for field_name, requirements in REQUIRED_TITLE_BLOCK_FIELDS.items():
            value = getattr(title_block, field_name, None)

            if value and str(value).strip():
                fields_present += 1
            else:
                fields_missing += 1
                severity = ValidationSeverity.CRITICAL if requirements["severity"] == "critical" else \
                           ValidationSeverity.ERROR if requirements["severity"] == "error" else \
                           ValidationSeverity.WARNING

                if requirements["required"]:
                    result.issues.append(ValidationIssue(
                        severity=severity,
                        check_type="title_block_missing",
                        message=f"Title block missing required field: {field_name}",
                        location="Title Block",
                        suggestion=f"Add {field_name} to title block",
                    ))

        result.title_block_fields_present = fields_present
        result.title_block_fields_missing = fields_missing

        # Determine title block completeness
        required_fields = [k for k, v in REQUIRED_TITLE_BLOCK_FIELDS.items() if v["required"]]
        required_present = sum(1 for f in required_fields if getattr(title_block, f, None))

        if required_present == len(required_fields):
            result.title_block_complete = True
            result.passed += 1
        elif required_present >= len(required_fields) * 0.7:
            result.warnings += 1
        else:
            result.failed += 1
            result.critical_failures += 1

    def _check_revision_history(self, extraction_result, result: CompletenessValidationResult):
        """Check revision history presence and completeness."""
        result.total_checks += 1

        revisions = extraction_result.revision_history
        result.revision_entries = len(revisions)

        if revisions:
            result.revision_history_present = True

            # Check that revisions have required info
            incomplete_revs = 0
            for rev in revisions:
                if not rev.revision or not rev.date:
                    incomplete_revs += 1

            if incomplete_revs > 0:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="revision_incomplete",
                    message=f"{incomplete_revs} revision entries missing date or revision letter",
                    location="Revision Block",
                    suggestion="Complete all revision history entries",
                ))
                result.warnings += 1
            else:
                result.passed += 1
        else:
            # Check if this is Rev 0 (initial release - no history expected)
            current_rev = extraction_result.title_block.revision or ""
            if current_rev.upper() in ["0", "A", "-", "INITIAL"]:
                result.revision_history_present = True
                result.passed += 1
            else:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="revision_history_missing",
                    message="No revision history found for non-initial revision",
                    location="Revision Block",
                    suggestion="Add revision history block with ECN information",
                ))
                result.warnings += 1

    def _check_general_notes(self, extraction_result, result: CompletenessValidationResult):
        """Check general notes presence and content."""
        result.total_checks += 1

        general_notes = extraction_result.general_notes
        result.general_notes_count = len(general_notes)

        if general_notes:
            result.general_notes_present = True

            # Check for required notes based on drawing type
            drawing_type = extraction_result.drawing_type
            if drawing_type:
                required = REQUIRED_NOTES_BY_TYPE.get(drawing_type.value, [])
                notes_text = " ".join([n.text.upper() for n in general_notes])

                missing_notes = []
                for req in required:
                    if req.upper() not in notes_text:
                        missing_notes.append(req)

                if missing_notes:
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        check_type="notes_incomplete",
                        message=f"General notes may be missing: {', '.join(missing_notes)}",
                        location="General Notes",
                        suggestion="Consider adding these common notes for this drawing type",
                    ))

            result.passed += 1
        else:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="general_notes_missing",
                message="No general notes found on drawing",
                location="General Notes",
                suggestion="Add general notes with material, weld, and finish specifications",
            ))
            result.warnings += 1

    def _check_shop_notes(self, extraction_result, result: CompletenessValidationResult):
        """Check shop/manufacturing notes presence."""
        result.total_checks += 1

        general_notes = extraction_result.general_notes

        # Look for shop-specific notes
        has_shop_notes = False
        shop_keywords = ["SHOP", "FABRICAT", "MANUFACTUR", "MACHINE", "WELD PREP", "FINISH"]

        if general_notes:
            notes_text = " ".join([n.text.upper() for n in general_notes])
            has_shop_notes = any(kw in notes_text for kw in shop_keywords)

        if has_shop_notes:
            result.passed += 1
        else:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="shop_notes_missing",
                message="No shop/fabrication notes detected",
                suggestion="Consider adding fabrication-specific instructions",
            ))
            result.passed += 1  # Not a failure, just informational

    def _check_weld_details(self, extraction_result, result: CompletenessValidationResult):
        """Check weld detail presence."""
        result.total_checks += 1

        weld_symbols = extraction_result.weld_symbols
        drawing_type = extraction_result.drawing_type

        if weld_symbols:
            result.weld_details_present = True
            result.passed += 1
        else:
            # For M-series and S-series, welds are typically expected
            if drawing_type and drawing_type.value in ["M", "S"]:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="weld_details_missing",
                    message="No weld symbols extracted from fabrication drawing",
                    suggestion="Verify weld symbols are present and legible",
                ))
                result.warnings += 1
            else:
                result.passed += 1

    def _check_section_views(self, extraction_result, result: CompletenessValidationResult):
        """Check for section views."""
        result.total_checks += 1

        # This would typically analyze the PDF layout
        # For now, check general notes for section references
        general_notes = extraction_result.general_notes

        section_keywords = VIEW_REQUIREMENTS["section"]["keywords"]
        notes_text = " ".join([n.text.upper() for n in general_notes]) if general_notes else ""

        if any(kw in notes_text for kw in section_keywords):
            result.section_views_present = True
            result.passed += 1
        else:
            # Check page count - multi-page drawings likely have sections
            if extraction_result.page_count > 1:
                result.section_views_present = True
                result.passed += 1
            else:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="section_views_not_found",
                    message="Section views not detected",
                    suggestion="Add section views for internal features if applicable",
                ))
                result.passed += 1

    def _check_detail_views(self, extraction_result, result: CompletenessValidationResult):
        """Check for detail views."""
        result.total_checks += 1

        general_notes = extraction_result.general_notes

        detail_keywords = VIEW_REQUIREMENTS["detail"]["keywords"]
        notes_text = " ".join([n.text.upper() for n in general_notes]) if general_notes else ""

        if any(kw in notes_text for kw in detail_keywords):
            result.detail_views_present = True
            result.passed += 1
        else:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="detail_views_not_found",
                message="Detail views not detected",
                suggestion="Add detail views for critical features",
            ))
            result.passed += 1

    def _check_scale(self, extraction_result, result: CompletenessValidationResult):
        """Check scale specification."""
        result.total_checks += 1

        title_block = extraction_result.title_block
        scale = title_block.scale

        if scale and scale.strip():
            # Validate scale format
            valid_scales = ["1:1", "1:2", "1:4", "1:5", "1:10", "1:20", "1:50", "1:100",
                           "2:1", "4:1", "5:1", "10:1",
                           "FULL", "HALF", "NTS", "AS NOTED", "VARIES"]

            scale_upper = scale.upper().replace(" ", "")

            is_valid = any(vs.replace(" ", "") in scale_upper for vs in valid_scales)

            if not is_valid:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="scale_unusual",
                    message=f"Unusual scale specification: {scale}",
                    suggestion="Verify scale is correct",
                ))

            result.passed += 1
        else:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="scale_missing",
                message="No scale specified in title block",
                location="Title Block",
                suggestion="Add scale to title block",
            ))
            result.warnings += 1

    def _check_projection_symbol(self, extraction_result, result: CompletenessValidationResult):
        """Check for projection symbol (third angle)."""
        result.total_checks += 1

        general_notes = extraction_result.general_notes
        notes_text = " ".join([n.text.upper() for n in general_notes]) if general_notes else ""

        # Look for third angle projection reference
        projection_keywords = ["THIRD ANGLE", "3RD ANGLE", "ANSI", "ISO-E", "PROJECTION"]

        if any(kw in notes_text for kw in projection_keywords):
            result.passed += 1
        else:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="projection_symbol_missing",
                message="Third angle projection symbol not detected",
                suggestion="Add projection symbol per ANSI/ASME Y14.3",
            ))
            result.passed += 1  # Informational only

    def _check_proprietary_notice(self, extraction_result, result: CompletenessValidationResult):
        """Check for proprietary/copyright notice."""
        result.total_checks += 1

        general_notes = extraction_result.general_notes
        title_block = extraction_result.title_block

        # Combine all text sources
        all_text = ""
        if general_notes:
            all_text += " ".join([n.text.upper() for n in general_notes])

        # Look for proprietary notices
        proprietary_keywords = ["PROPRIETARY", "CONFIDENTIAL", "COPYRIGHT", "DO NOT COPY",
                               "PROPERTY OF", "ALL RIGHTS RESERVED"]

        if any(kw in all_text for kw in proprietary_keywords):
            result.passed += 1
        else:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="proprietary_notice_missing",
                message="No proprietary/copyright notice detected",
                suggestion="Consider adding proprietary notice for company drawings",
            ))
            result.passed += 1  # Informational only

    def to_dict(self, result: CompletenessValidationResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "completeness",
            "total_checks": result.total_checks,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "critical_failures": result.critical_failures,
            "statistics": {
                "title_block_complete": result.title_block_complete,
                "title_block_fields_present": result.title_block_fields_present,
                "title_block_fields_missing": result.title_block_fields_missing,
                "revision_history_present": result.revision_history_present,
                "revision_entries": result.revision_entries,
                "general_notes_present": result.general_notes_present,
                "general_notes_count": result.general_notes_count,
                "bom_present": result.bom_present,
                "bom_items": result.bom_items,
                "weld_details_present": result.weld_details_present,
                "section_views_present": result.section_views_present,
                "detail_views_present": result.detail_views_present,
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
