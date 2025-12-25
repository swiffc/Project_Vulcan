"""
GD&T (Geometric Dimensioning & Tolerancing) Parser
==================================================
Parses and validates GD&T symbols per ASME Y14.5-2018.

Critical Features:
- Feature control frame parsing
- Datum reference frame validation
- Position tolerance with MMC/LMC bonus
- Form tolerances (flatness, straightness, circularity, cylindricity)
- Orientation tolerances (perpendicularity, parallelism, angularity)
- Profile and runout tolerances

References:
- ASME Y14.5-2018 Dimensioning and Tolerancing
- ISO 1101 Geometrical Tolerancing

Usage:
    from agents.cad_agent.adapters.gdt_parser import GDTParser, validate_feature_control_frame
    
    parser = GDTParser()
    result = parser.parse_drawing_text(ocr_text)
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import re
import logging

logger = logging.getLogger("cad_agent.gdt-parser")


# =============================================================================
# GD&T SYMBOLS (Unicode)
# =============================================================================

GDT_SYMBOLS = {
    # Form tolerances
    "flatness": "⏥",
    "straightness": "—",
    "circularity": "○",
    "cylindricity": "⌭",
    
    # Orientation tolerances
    "perpendicularity": "⊥",
    "parallelism": "∥",
    "angularity": "∠",
    
    # Location tolerances
    "position": "⊕",
    "concentricity": "◎",
    "symmetry": "⌯",
    
    # Profile tolerances
    "profile_surface": "⌓",
    "profile_line": "⌒",
    
    # Runout tolerances
    "circular_runout": "↗",
    "total_runout": "↗↗",
    
    # Material condition modifiers
    "mmc": "Ⓜ",  # Maximum Material Condition
    "lmc": "Ⓛ",  # Least Material Condition
    "rfs": "",    # Regardless of Feature Size (default)
    
    # Datum
    "datum": "▭",
}

# Alternate text representations
GDT_TEXT_SYMBOLS = {
    "flatness": ["FLATNESS", "FLAT", "FLT"],
    "straightness": ["STRAIGHTNESS", "STR"],
    "circularity": ["CIRCULARITY", "ROUNDNESS", "CIRC"],
    "cylindricity": ["CYLINDRICITY", "CYL"],
    "perpendicularity": ["PERPENDICULARITY", "PERP", "⊥"],
    "parallelism": ["PARALLELISM", "PARA", "∥", "//"],
    "angularity": ["ANGULARITY", "ANG"],
    "position": ["POSITION", "POS", "TRUE POSITION", "TP"],
    "concentricity": ["CONCENTRICITY", "CONC"],
    "symmetry": ["SYMMETRY", "SYM"],
    "profile_surface": ["PROFILE OF A SURFACE", "PROFILE SURF"],
    "profile_line": ["PROFILE OF A LINE", "PROFILE LINE"],
    "circular_runout": ["CIRCULAR RUNOUT", "CIRC RO"],
    "total_runout": ["TOTAL RUNOUT", "TOT RO"],
}


class ToleranceType(Enum):
    """GD&T tolerance types per ASME Y14.5."""
    # Form
    FLATNESS = "flatness"
    STRAIGHTNESS = "straightness"
    CIRCULARITY = "circularity"
    CYLINDRICITY = "cylindricity"
    
    # Orientation
    PERPENDICULARITY = "perpendicularity"
    PARALLELISM = "parallelism"
    ANGULARITY = "angularity"
    
    # Location
    POSITION = "position"
    CONCENTRICITY = "concentricity"
    SYMMETRY = "symmetry"
    
    # Profile
    PROFILE_SURFACE = "profile_surface"
    PROFILE_LINE = "profile_line"
    
    # Runout
    CIRCULAR_RUNOUT = "circular_runout"
    TOTAL_RUNOUT = "total_runout"


class MaterialCondition(Enum):
    """Material condition modifiers."""
    MMC = "mmc"  # Maximum Material Condition
    LMC = "lmc"  # Least Material Condition
    RFS = "rfs"  # Regardless of Feature Size (default)


class DatumPrecedence(Enum):
    """Datum precedence in reference frame."""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"


@dataclass
class Datum:
    """Datum feature definition."""
    label: str  # A, B, C, etc.
    precedence: DatumPrecedence
    modifier: MaterialCondition = MaterialCondition.RFS
    is_target: bool = False  # Datum target (point, line, area)
    target_info: Optional[str] = None


@dataclass
class FeatureControlFrame:
    """
    Feature control frame per ASME Y14.5.
    
    Example: |⊕|Ø0.010|Ⓜ|A|B|Ⓜ|C|
    """
    tolerance_type: ToleranceType
    tolerance_value: float  # in inches or mm
    tolerance_unit: str = "in"
    feature_modifier: MaterialCondition = MaterialCondition.RFS
    datum_primary: Optional[Datum] = None
    datum_secondary: Optional[Datum] = None
    datum_tertiary: Optional[Datum] = None
    is_diameter: bool = False  # Ø symbol present
    is_spherical: bool = False  # S symbol present
    is_statistical: bool = False  # ST symbol present
    
    @property
    def has_datums(self) -> bool:
        """Check if any datums are specified."""
        return any([self.datum_primary, self.datum_secondary, self.datum_tertiary])
    
    @property
    def datum_count(self) -> int:
        """Number of datums in reference frame."""
        return sum([
            self.datum_primary is not None,
            self.datum_secondary is not None,
            self.datum_tertiary is not None
        ])


@dataclass
class GDTValidationResult:
    """Result of GD&T validation."""
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)
    frames_found: int = 0
    datums_found: list[str] = field(default_factory=list)


@dataclass
class PositionToleranceAnalysis:
    """Analysis of position tolerance with bonus tolerance."""
    nominal_tolerance: float
    feature_size_actual: float
    feature_size_mmc: float
    bonus_tolerance: float  # When MMC applied
    total_tolerance: float  # Nominal + bonus
    virtual_condition: float  # Boundary for functional gauging


# =============================================================================
# GD&T PARSER
# =============================================================================

class GDTParser:
    """
    Parse GD&T symbols from engineering drawings.
    
    Handles:
    - OCR text extraction of symbols
    - Feature control frame interpretation
    - Datum reference frame validation
    - Bonus tolerance calculation (MMC/LMC)
    """
    
    def __init__(self):
        self.frames: list[FeatureControlFrame] = []
        self.datums: dict[str, Datum] = {}
    
    def parse_drawing_text(self, text: str) -> GDTValidationResult:
        """
        Parse GD&T from drawing text (OCR output).
        
        Args:
            text: OCR extracted text from drawing
            
        Returns:
            GDTValidationResult with found frames and validation
        """
        result = GDTValidationResult(is_valid=True)
        
        # Find feature control frames
        self.frames = self._extract_feature_control_frames(text)
        result.frames_found = len(self.frames)
        
        # Find datum definitions
        self.datums = self._extract_datums(text)
        result.datums_found = list(self.datums.keys())
        
        # Validate each frame
        for frame in self.frames:
            frame_errors = self._validate_frame(frame)
            result.errors.extend(frame_errors)
        
        # Check for common issues
        result.warnings.extend(self._check_common_issues())
        
        result.is_valid = len(result.errors) == 0
        
        logger.info(f"GD&T parsing: {result.frames_found} frames, {len(result.datums_found)} datums")
        
        return result
    
    def _extract_feature_control_frames(self, text: str) -> list[FeatureControlFrame]:
        """Extract feature control frames from text."""
        frames = []
        
        # Pattern: |SYMBOL|TOLERANCE|MODIFIER|DATUM_A|DATUM_B|DATUM_C|
        # Simple extraction - real implementation would be more sophisticated
        
        for tol_type in ToleranceType:
            # Check for text representations
            for text_symbol in GDT_TEXT_SYMBOLS.get(tol_type.value, []):
                pattern = rf"{text_symbol}\s+(Ø|DIA)?\s*([0-9.]+)\s*(MMC|LMC|RFS)?"
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    is_dia = match.group(1) is not None
                    value = float(match.group(2))
                    modifier_str = match.group(3) or "RFS"
                    
                    modifier = MaterialCondition.RFS
                    if "MMC" in modifier_str.upper():
                        modifier = MaterialCondition.MMC
                    elif "LMC" in modifier_str.upper():
                        modifier = MaterialCondition.LMC
                    
                    frame = FeatureControlFrame(
                        tolerance_type=tol_type,
                        tolerance_value=value,
                        is_diameter=is_dia,
                        feature_modifier=modifier
                    )
                    
                    # Try to extract datums (simplified)
                    # Real implementation would parse datum references after tolerance
                    datum_match = re.search(r"DATUM\s+([A-Z])", text[match.end():match.end()+50])
                    if datum_match:
                        datum_label = datum_match.group(1)
                        if datum_label in self.datums:
                            frame.datum_primary = self.datums[datum_label]
                    
                    frames.append(frame)
        
        return frames
    
    def _extract_datums(self, text: str) -> dict[str, Datum]:
        """Extract datum definitions from text."""
        datums = {}
        
        # Pattern: DATUM A, DATUM B, etc.
        pattern = r"DATUM\s+([A-Z])(?:\s+(MMC|LMC))?"
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        precedence_order = [DatumPrecedence.PRIMARY, DatumPrecedence.SECONDARY, DatumPrecedence.TERTIARY]
        precedence_idx = 0
        
        for match in matches:
            label = match.group(1)
            modifier_str = match.group(2) or "RFS"
            
            modifier = MaterialCondition.RFS
            if modifier_str.upper() == "MMC":
                modifier = MaterialCondition.MMC
            elif modifier_str.upper() == "LMC":
                modifier = MaterialCondition.LMC
            
            precedence = precedence_order[precedence_idx] if precedence_idx < 3 else DatumPrecedence.TERTIARY
            
            datum = Datum(
                label=label,
                precedence=precedence,
                modifier=modifier
            )
            
            datums[label] = datum
            precedence_idx += 1
        
        return datums
    
    def _validate_frame(self, frame: FeatureControlFrame) -> list[str]:
        """Validate a feature control frame."""
        errors = []
        
        # Check if datums are required for this tolerance type
        requires_datum = frame.tolerance_type in [
            ToleranceType.PERPENDICULARITY,
            ToleranceType.PARALLELISM,
            ToleranceType.ANGULARITY,
            ToleranceType.POSITION,
        ]
        
        if requires_datum and not frame.has_datums:
            errors.append(
                f"{frame.tolerance_type.value} tolerance requires datum reference frame"
            )
        
        # Check datum precedence
        if frame.datum_secondary and not frame.datum_primary:
            errors.append("Secondary datum specified without primary datum")
        
        if frame.datum_tertiary and not frame.datum_secondary:
            errors.append("Tertiary datum specified without secondary datum")
        
        # Validate tolerance value
        if frame.tolerance_value <= 0:
            errors.append(f"Invalid tolerance value: {frame.tolerance_value}")
        
        # Check modifier applicability
        if frame.tolerance_type in [ToleranceType.FLATNESS, ToleranceType.STRAIGHTNESS]:
            if frame.feature_modifier != MaterialCondition.RFS:
                errors.append(f"{frame.tolerance_type.value} does not use material condition modifiers")
        
        return errors
    
    def _check_common_issues(self) -> list[str]:
        """Check for common GD&T issues."""
        warnings = []
        
        # Check if datums are defined but not used
        used_datums = set()
        for frame in self.frames:
            if frame.datum_primary:
                used_datums.add(frame.datum_primary.label)
            if frame.datum_secondary:
                used_datums.add(frame.datum_secondary.label)
            if frame.datum_tertiary:
                used_datums.add(frame.datum_tertiary.label)
        
        unused_datums = set(self.datums.keys()) - used_datums
        if unused_datums:
            warnings.append(f"Datums defined but not used: {', '.join(sorted(unused_datums))}")
        
        # Check for missing datum definitions
        for frame in self.frames:
            for datum in [frame.datum_primary, frame.datum_secondary, frame.datum_tertiary]:
                if datum and datum.label not in self.datums:
                    warnings.append(f"Datum {datum.label} referenced but not defined")
        
        return warnings
    
    def calculate_position_bonus(
        self,
        nominal_tolerance: float,
        feature_size_actual: float,
        feature_size_mmc: float,
        is_hole: bool = True
    ) -> PositionToleranceAnalysis:
        """
        Calculate bonus tolerance for position at MMC.
        
        For holes: MMC = smallest hole size
        For shafts: MMC = largest shaft size
        
        Bonus tolerance = |Actual size - MMC size|
        Total tolerance = Nominal + Bonus
        """
        if is_hole:
            # For holes: actual > MMC gives bonus (bigger hole = more tolerance)
            bonus = max(0, feature_size_actual - feature_size_mmc)
            virtual_condition = feature_size_mmc - nominal_tolerance
        else:
            # For shafts: actual < MMC gives bonus (smaller shaft = more tolerance)
            bonus = max(0, feature_size_mmc - feature_size_actual)
            virtual_condition = feature_size_mmc + nominal_tolerance
        
        total = nominal_tolerance + bonus
        
        return PositionToleranceAnalysis(
            nominal_tolerance=nominal_tolerance,
            feature_size_actual=feature_size_actual,
            feature_size_mmc=feature_size_mmc,
            bonus_tolerance=bonus,
            total_tolerance=total,
            virtual_condition=virtual_condition
        )


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_feature_control_frame(
    tolerance_type: str,
    tolerance_value: float,
    datums: list[str],
    modifier: str = "RFS"
) -> tuple[bool, list[str]]:
    """
    Validate a feature control frame.
    
    Args:
        tolerance_type: Type of tolerance (position, perpendicularity, etc.)
        tolerance_value: Tolerance zone size
        datums: List of datum labels (e.g., ['A', 'B', 'C'])
        modifier: Material condition (MMC, LMC, RFS)
    
    Returns:
        (is_valid, error_messages)
    """
    errors = []
    
    # Validate tolerance type
    valid_types = [t.value for t in ToleranceType]
    if tolerance_type.lower() not in valid_types:
        errors.append(f"Invalid tolerance type: {tolerance_type}")
    
    # Validate tolerance value
    if tolerance_value <= 0:
        errors.append(f"Tolerance value must be positive: {tolerance_value}")
    
    # Validate datums for orientation/location tolerances
    requires_datum = tolerance_type.lower() in [
        "perpendicularity", "parallelism", "angularity", "position"
    ]
    if requires_datum and not datums:
        errors.append(f"{tolerance_type} requires datum reference")
    
    # Validate modifier
    valid_modifiers = ["MMC", "LMC", "RFS"]
    if modifier.upper() not in valid_modifiers:
        errors.append(f"Invalid material condition: {modifier}")
    
    return len(errors) == 0, errors


def check_datum_completeness(
    primary: Optional[str],
    secondary: Optional[str],
    tertiary: Optional[str]
) -> tuple[bool, list[str]]:
    """
    Check datum reference frame completeness.
    
    3-2-1 rule: Primary (3 points), Secondary (2 points), Tertiary (1 point)
    """
    warnings = []
    
    if secondary and not primary:
        warnings.append("Secondary datum without primary datum")
    
    if tertiary and not secondary:
        warnings.append("Tertiary datum without secondary datum")
    
    # Recommend complete datum reference frame for position
    if primary and not secondary:
        warnings.append("Consider adding secondary datum for complete constraint")
    
    if primary and secondary and not tertiary:
        warnings.append("Consider adding tertiary datum for full 3-2-1 constraint")
    
    return len(warnings) == 0, warnings


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "GDTParser",
    "ToleranceType",
    "MaterialCondition",
    "DatumPrecedence",
    "Datum",
    "FeatureControlFrame",
    "GDTValidationResult",
    "PositionToleranceAnalysis",
    "validate_feature_control_frame",
    "check_datum_completeness",
    "GDT_SYMBOLS",
]
