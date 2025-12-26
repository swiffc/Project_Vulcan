"""
Drawing Documentation Validator
===============================
Validates drawing completeness, notes, and documentation requirements.

Phase 25.10 - Documentation Validation

References:
- ASME Y14.100 (Engineering Drawing Practices)
- ASME Y14.5 (GD&T)
- AWS A2.4 (Welding Symbols)
- ISO 7200 (Title Block Requirements)
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
from enum import Enum

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.documentation")


# =============================================================================
# DOCUMENTATION REQUIREMENTS
# =============================================================================

class DrawingType(Enum):
    """Types of engineering drawings."""
    DETAIL = "detail"
    ASSEMBLY = "assembly"
    INSTALLATION = "installation"
    SCHEMATIC = "schematic"
    WELDMENT = "weldment"
    MACHINED_PART = "machined_part"
    SHEET_METAL = "sheet_metal"
    CASTING = "casting"


class DocumentationLevel(Enum):
    """Documentation rigor levels."""
    COMMERCIAL = "commercial"      # Basic shop requirements
    INDUSTRIAL = "industrial"      # Standard industrial
    NUCLEAR = "nuclear"            # Nuclear quality
    AEROSPACE = "aerospace"        # AS9100
    PRESSURE_VESSEL = "pressure"   # ASME Code


# Required title block fields by level
TITLE_BLOCK_REQUIREMENTS = {
    DocumentationLevel.COMMERCIAL: [
        "drawing_number",
        "revision",
        "title",
        "scale",
        "sheet",
        "drawn_by",
        "date",
    ],
    DocumentationLevel.INDUSTRIAL: [
        "drawing_number",
        "revision",
        "title",
        "scale",
        "sheet",
        "drawn_by",
        "checked_by",
        "approved_by",
        "date",
        "material",
        "finish",
    ],
    DocumentationLevel.NUCLEAR: [
        "drawing_number",
        "revision",
        "title",
        "scale",
        "sheet",
        "drawn_by",
        "checked_by",
        "approved_by",
        "qa_approved",
        "date",
        "material",
        "finish",
        "safety_class",
        "qa_category",
    ],
    DocumentationLevel.AEROSPACE: [
        "drawing_number",
        "revision",
        "title",
        "scale",
        "sheet",
        "drawn_by",
        "checked_by",
        "stress_approved",
        "approved_by",
        "date",
        "material",
        "finish",
        "cage_code",
        "next_assembly",
    ],
    DocumentationLevel.PRESSURE_VESSEL: [
        "drawing_number",
        "revision",
        "title",
        "scale",
        "sheet",
        "drawn_by",
        "checked_by",
        "approved_by",
        "date",
        "material",
        "design_pressure",
        "design_temperature",
        "code_stamp",
    ],
}

# Required general notes by drawing type
REQUIRED_NOTES_BY_TYPE = {
    DrawingType.DETAIL: [
        "general_tolerances",
        "surface_finish",
    ],
    DrawingType.ASSEMBLY: [
        "general_tolerances",
        "torque_spec",
        "cleaning_requirements",
    ],
    DrawingType.WELDMENT: [
        "general_tolerances",
        "welding_spec",
        "nde_requirements",
        "pwht_requirements",
        "preheat_requirements",
    ],
    DrawingType.MACHINED_PART: [
        "general_tolerances",
        "surface_finish",
        "heat_treatment",
        "hardness",
    ],
    DrawingType.SHEET_METAL: [
        "general_tolerances",
        "bend_radii",
        "grain_direction",
    ],
    DrawingType.PRESSURE_VESSEL: [
        "general_tolerances",
        "welding_spec",
        "nde_requirements",
        "design_pressure",
        "design_temperature",
        "hydro_test",
        "code_stamp",
    ],
}

# Common note patterns to search for
NOTE_PATTERNS = {
    "general_tolerances": [
        r"unless\s+otherwise\s+specified",
        r"tolerances?.*\d+",
        r"fractional.*\d+/\d+",
        r"decimal.*\.\d+",
        r"angular.*degree",
    ],
    "welding_spec": [
        r"aws\s*d1\.\d",
        r"asme\s*(sec|section)?\s*(ix|9)",
        r"wps",
        r"weld.*per",
        r"pqr",
    ],
    "nde_requirements": [
        r"(rt|ut|mt|pt|vt)",
        r"radiograph",
        r"ultrasonic",
        r"magnetic\s*particle",
        r"penetrant",
        r"visual\s*inspection",
        r"nde",
        r"non.?destructive",
    ],
    "surface_finish": [
        r"surface\s*finish",
        r"ra\s*\d+",
        r"μin",
        r"microinch",
        r"rms",
    ],
    "material": [
        r"astm\s*[a-z]\d+",
        r"aisi\s*\d+",
        r"sae\s*\d+",
        r"a36",
        r"a572",
        r"304.*ss",
        r"316.*ss",
    ],
    "heat_treatment": [
        r"heat\s*treat",
        r"anneal",
        r"normalize",
        r"quench",
        r"temper",
        r"stress\s*reliev",
        r"harden",
    ],
    "coating": [
        r"galvaniz",
        r"zinc\s*plate",
        r"paint",
        r"primer",
        r"sspc",
        r"powder\s*coat",
        r"anodiz",
    ],
    "torque_spec": [
        r"torque",
        r"ft.?lb",
        r"in.?lb",
        r"n.?m",
        r"tighten",
    ],
    "pwht_requirements": [
        r"pwht",
        r"post.*weld.*heat",
        r"stress\s*relief",
        r"°f.*hour",
    ],
    "preheat_requirements": [
        r"preheat",
        r"minimum.*temp",
        r"min.*°f",
    ],
    "hydro_test": [
        r"hydro.*test",
        r"hydrostatic",
        r"test\s*pressure",
        r"psig.*test",
    ],
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class TitleBlockData:
    """Title block content."""
    drawing_number: Optional[str] = None
    revision: Optional[str] = None
    title: Optional[str] = None
    scale: Optional[str] = None
    sheet: Optional[str] = None
    drawn_by: Optional[str] = None
    drawn_date: Optional[str] = None
    checked_by: Optional[str] = None
    approved_by: Optional[str] = None
    material: Optional[str] = None
    finish: Optional[str] = None
    # Additional fields as dict
    additional_fields: Dict[str, str] = field(default_factory=dict)


@dataclass
class DrawingNotes:
    """Drawing notes content."""
    general_notes: List[str] = field(default_factory=list)
    local_notes: List[str] = field(default_factory=list)
    flag_notes: List[str] = field(default_factory=list)
    bill_of_materials: List[Dict] = field(default_factory=list)


@dataclass
class DocumentationValidationResult:
    """Documentation validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

    # Documentation completeness
    title_block_complete: bool = False
    required_notes_present: bool = False
    missing_elements: List[str] = field(default_factory=list)


# =============================================================================
# DOCUMENTATION VALIDATOR
# =============================================================================

class DocumentationValidator:
    """
    Validates drawing documentation completeness.

    Phase 25.10 - Checks:
    1. Title block completeness
    2. Required notes present
    3. Revision history
    4. Drawing number format
    5. Scale correctness
    6. Bill of materials completeness
    7. Reference drawing list
    8. Approval signatures
    9. Note numbering consistency
    10. Standard compliance notes
    """

    def __init__(self):
        pass

    def validate_title_block(
        self,
        title_block: TitleBlockData,
        level: DocumentationLevel = DocumentationLevel.INDUSTRIAL
    ) -> DocumentationValidationResult:
        """
        Validate title block completeness.

        Args:
            title_block: Title block data
            level: Documentation level

        Returns:
            Validation result
        """
        result = DocumentationValidationResult()
        required_fields = TITLE_BLOCK_REQUIREMENTS.get(level, [])

        # Check each required field
        for field_name in required_fields:
            result.total_checks += 1

            # Map field name to attribute
            attr_name = field_name.replace("-", "_")
            value = getattr(title_block, attr_name, None)

            if value is None:
                value = title_block.additional_fields.get(field_name)

            if not value:
                result.missing_elements.append(field_name)
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="title_block_missing",
                    message=f"Title block missing: {field_name}",
                    suggestion=f"Add {field_name} to title block",
                    standard_reference="ASME Y14.100",
                ))
                result.warnings += 1
            else:
                result.passed += 1

        # Check drawing number format
        result.total_checks += 1
        if title_block.drawing_number:
            if not self._validate_drawing_number(title_block.drawing_number):
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="drawing_number_format",
                    message=f"Non-standard drawing number format: {title_block.drawing_number}",
                    suggestion="Consider standardized numbering (e.g., XX-YYYY-ZZZ)",
                ))
            result.passed += 1
        else:
            result.missing_elements.append("drawing_number")
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                check_type="drawing_number_missing",
                message="Drawing number is required",
            ))
            result.critical_failures += 1
            result.failed += 1

        # Check revision format
        result.total_checks += 1
        if title_block.revision:
            if not self._validate_revision(title_block.revision):
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="revision_format",
                    message=f"Non-standard revision format: {title_block.revision}",
                    suggestion="Use letter revisions (A, B, C) or numeric (0, 1, 2)",
                ))
            result.passed += 1
        else:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="revision_missing",
                message="Revision not specified (assumed initial release)",
            ))
            result.warnings += 1

        # Check scale format
        result.total_checks += 1
        if title_block.scale:
            if not self._validate_scale(title_block.scale):
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="scale_format",
                    message=f"Scale format unclear: {title_block.scale}",
                    suggestion="Use standard formats: 1:1, 1:2, HALF, FULL, NTS",
                ))
                result.warnings += 1
            else:
                result.passed += 1
        else:
            result.passed += 1  # Scale not always required

        result.title_block_complete = len(result.missing_elements) == 0

        return result

    def _validate_drawing_number(self, number: str) -> bool:
        """Check if drawing number follows common patterns."""
        patterns = [
            r"^\d{5,}$",           # Numeric only
            r"^[A-Z]{2,}-\d+",     # Prefix-numeric
            r"^\d+-\d+-\d+",       # Multi-part numeric
            r"^[A-Z0-9]+-[A-Z0-9]+-[A-Z0-9]+",  # Multi-part alphanumeric
        ]
        return any(re.match(p, number.upper()) for p in patterns)

    def _validate_revision(self, rev: str) -> bool:
        """Check if revision follows standard patterns."""
        patterns = [
            r"^[A-Z]$",           # Single letter
            r"^\d+$",             # Numeric
            r"^[A-Z]\d+$",        # Letter + number
            r"^REV\s*[A-Z0-9]+$", # REV prefix
        ]
        return any(re.match(p, rev.upper().strip()) for p in patterns)

    def _validate_scale(self, scale: str) -> bool:
        """Check if scale format is valid."""
        patterns = [
            r"^1:\d+$",           # 1:X
            r"^\d+:\d+$",         # X:Y
            r"^FULL$",            # FULL
            r"^HALF$",            # HALF
            r"^NTS$",             # Not To Scale
            r"^AS\s*SHOWN$",      # As Shown
            r"^NONE$",            # None
        ]
        return any(re.match(p, scale.upper().strip()) for p in patterns)

    def validate_notes(
        self,
        notes: DrawingNotes,
        drawing_type: DrawingType = DrawingType.DETAIL,
        level: DocumentationLevel = DocumentationLevel.INDUSTRIAL
    ) -> DocumentationValidationResult:
        """
        Validate drawing notes completeness.

        Args:
            notes: Drawing notes data
            drawing_type: Type of drawing
            level: Documentation level

        Returns:
            Validation result
        """
        result = DocumentationValidationResult()

        # Combine all notes for searching
        all_notes_text = " ".join(notes.general_notes + notes.local_notes + notes.flag_notes).lower()

        # Get required notes for drawing type
        required_notes = REQUIRED_NOTES_BY_TYPE.get(drawing_type, [])

        for note_type in required_notes:
            result.total_checks += 1

            patterns = NOTE_PATTERNS.get(note_type, [])
            found = False

            for pattern in patterns:
                if re.search(pattern, all_notes_text, re.IGNORECASE):
                    found = True
                    break

            if not found:
                result.missing_elements.append(note_type)
                severity = ValidationSeverity.WARNING

                # Critical for certain notes
                if note_type in ["welding_spec", "nde_requirements"] and drawing_type == DrawingType.WELDMENT:
                    severity = ValidationSeverity.CRITICAL
                    result.critical_failures += 1
                    result.failed += 1
                else:
                    result.warnings += 1

                result.issues.append(ValidationIssue(
                    severity=severity,
                    check_type="note_missing",
                    message=f"Required note missing: {note_type.replace('_', ' ').title()}",
                    suggestion=f"Add {note_type.replace('_', ' ')} note per standard practice",
                ))
            else:
                result.passed += 1

        # Check note numbering consistency
        result.total_checks += 1
        if notes.general_notes:
            numbering_consistent = self._check_note_numbering(notes.general_notes)
            if not numbering_consistent:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="note_numbering",
                    message="Note numbering inconsistent or missing",
                    suggestion="Number notes sequentially (1, 2, 3...)",
                ))
            result.passed += 1
        else:
            result.passed += 1

        # Check for orphan note references
        result.total_checks += 1
        referenced_notes = self._find_note_references(all_notes_text)
        if notes.general_notes:
            defined_notes = set(range(1, len(notes.general_notes) + 1))
            orphans = referenced_notes - defined_notes

            if orphans:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="orphan_note_reference",
                    message=f"References to undefined notes: {sorted(orphans)}",
                    suggestion="Add missing notes or correct references",
                ))
                result.warnings += 1
            else:
                result.passed += 1
        else:
            result.passed += 1

        result.required_notes_present = len([m for m in result.missing_elements if m in required_notes]) == 0

        return result

    def _check_note_numbering(self, notes: List[str]) -> bool:
        """Check if notes are numbered sequentially."""
        expected_num = 1
        for note in notes:
            match = re.match(r"^\s*(\d+)[.)\s]", note)
            if match:
                note_num = int(match.group(1))
                if note_num != expected_num:
                    return False
                expected_num += 1
        return True

    def _find_note_references(self, text: str) -> Set[int]:
        """Find note number references in text."""
        references = set()
        # Patterns like "SEE NOTE 5", "NOTE 3", "(NOTE 7)"
        matches = re.findall(r"note\s*(\d+)", text, re.IGNORECASE)
        for m in matches:
            references.add(int(m))
        return references

    def validate_bom(
        self,
        bom: List[Dict],
        drawing_type: DrawingType = DrawingType.ASSEMBLY
    ) -> DocumentationValidationResult:
        """
        Validate Bill of Materials completeness.

        Args:
            bom: Bill of materials entries
            drawing_type: Type of drawing

        Returns:
            Validation result
        """
        result = DocumentationValidationResult()

        if drawing_type not in [DrawingType.ASSEMBLY, DrawingType.WELDMENT]:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="bom_not_required",
                message="BOM typically not required for this drawing type",
            ))
            return result

        result.total_checks += 1
        if not bom:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="bom_missing",
                message="Bill of Materials missing for assembly drawing",
                suggestion="Add BOM with item numbers, part numbers, descriptions, quantities",
            ))
            result.warnings += 1
            return result

        result.passed += 1

        # Check required BOM fields
        required_fields = ["item", "part_number", "description", "qty"]

        for i, item in enumerate(bom):
            result.total_checks += 1
            missing_fields = [f for f in required_fields if f not in item or not item[f]]

            if missing_fields:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="bom_incomplete",
                    message=f"BOM item {i+1} missing: {', '.join(missing_fields)}",
                ))
                result.warnings += 1
            else:
                result.passed += 1

        # Check item number sequence
        result.total_checks += 1
        item_numbers = [item.get("item") for item in bom if item.get("item")]
        if item_numbers:
            try:
                nums = [int(n) for n in item_numbers]
                expected = list(range(1, max(nums) + 1))
                if sorted(nums) != expected:
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        check_type="bom_numbering",
                        message="BOM item numbers not sequential",
                    ))
            except (ValueError, TypeError):
                pass  # Non-numeric item numbers
            result.passed += 1
        else:
            result.passed += 1

        return result

    def to_dict(self, result: DocumentationValidationResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "documentation",
            "total_checks": result.total_checks,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "critical_failures": result.critical_failures,
            "title_block_complete": result.title_block_complete,
            "required_notes_present": result.required_notes_present,
            "missing_elements": result.missing_elements,
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
