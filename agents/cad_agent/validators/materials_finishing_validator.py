"""
Materials & Surface Finishing Validator
========================================
Validates material specifications, surface treatments, coatings, and finishes.

Phase 25.6 - Materials Analysis

References:
- SSPC (Society for Protective Coatings) Standards
- ASTM Material Specifications
- AWS D1.1 (Material compatibility)
- AISC (Galvanizing requirements)
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.materials")


# =============================================================================
# MATERIAL SPECIFICATIONS
# =============================================================================

class MaterialCategory(Enum):
    """Material categories."""
    CARBON_STEEL = "carbon_steel"
    ALLOY_STEEL = "alloy_steel"
    STAINLESS_STEEL = "stainless_steel"
    ALUMINUM = "aluminum"
    COPPER = "copper"
    CAST_IRON = "cast_iron"
    PLASTIC = "plastic"


# Common steel specifications with properties
STEEL_SPECIFICATIONS = {
    # Spec: (min_yield_ksi, min_tensile_ksi, weldability, P_number)
    "A36": (36, 58, "excellent", "1"),
    "A572-50": (50, 65, "excellent", "1"),
    "A572-65": (65, 80, "good", "1"),
    "A588": (50, 70, "excellent", "1"),  # Weathering steel
    "A514": (100, 110, "fair", "5B"),    # Quenched & tempered
    "A992": (50, 65, "excellent", "1"),  # W-shapes
    "A500B": (46, 58, "excellent", "1"), # HSS
    "A500C": (50, 62, "excellent", "1"), # HSS
    "A53B": (35, 60, "excellent", "1"),  # Pipe
    "A516-70": (38, 70, "excellent", "1"), # Pressure vessel
    "A240-304": (30, 75, "excellent", "8"), # Stainless
    "A240-316": (30, 75, "excellent", "8"), # Stainless
}

# Stainless steel grades and properties
STAINLESS_GRADES = {
    # Grade: (category, corrosion_resistance, max_service_temp_f)
    "304": ("austenitic", "good", 1500),
    "304L": ("austenitic", "good", 1500),
    "316": ("austenitic", "excellent", 1500),
    "316L": ("austenitic", "excellent", 1500),
    "321": ("austenitic", "good", 1600),  # Ti stabilized
    "347": ("austenitic", "good", 1600),  # Nb stabilized
    "410": ("martensitic", "fair", 1200),
    "430": ("ferritic", "fair", 1500),
    "2205": ("duplex", "excellent", 600),
    "2507": ("super_duplex", "excellent", 600),
}


# =============================================================================
# SURFACE PREPARATION STANDARDS
# =============================================================================

class SurfacePrep(Enum):
    """Surface preparation levels per SSPC."""
    SP1 = "solvent_cleaning"       # SSPC-SP 1
    SP2 = "hand_tool_cleaning"     # SSPC-SP 2
    SP3 = "power_tool_cleaning"    # SSPC-SP 3
    SP5 = "white_metal_blast"      # SSPC-SP 5 (Sa 3)
    SP6 = "commercial_blast"       # SSPC-SP 6 (Sa 2)
    SP7 = "brush_off_blast"        # SSPC-SP 7 (Sa 1)
    SP10 = "near_white_blast"      # SSPC-SP 10 (Sa 2.5)
    SP11 = "power_tool_bare_metal" # SSPC-SP 11
    SP14 = "industrial_blast"      # SSPC-SP 14


# Surface prep requirements by coating type
COATING_PREP_REQUIREMENTS = {
    # Coating type: (min_prep, optimal_prep, profile_mils_min, profile_mils_max)
    "alkyd_primer": (SurfacePrep.SP2, SurfacePrep.SP6, 1.0, 3.0),
    "epoxy_primer": (SurfacePrep.SP6, SurfacePrep.SP10, 1.5, 3.5),
    "zinc_rich_primer": (SurfacePrep.SP10, SurfacePrep.SP5, 2.0, 4.0),
    "hot_dip_galvanizing": (SurfacePrep.SP1, SurfacePrep.SP1, 0, 0),  # Acid cleaning
    "powder_coating": (SurfacePrep.SP6, SurfacePrep.SP10, 1.0, 2.5),
    "paint_waterborne": (SurfacePrep.SP2, SurfacePrep.SP6, 1.0, 2.5),
    "polyurethane": (SurfacePrep.SP10, SurfacePrep.SP5, 2.0, 4.0),
    "metallizing": (SurfacePrep.SP5, SurfacePrep.SP5, 3.0, 5.0),
}


# =============================================================================
# COATING SYSTEMS
# =============================================================================

# Standard coating systems with DFT (Dry Film Thickness)
COATING_SYSTEMS = {
    # System ID: {layers, total_dft_mils, service_environment}
    "C1": {
        "layers": [("zinc_rich_primer", 3), ("epoxy_midcoat", 5), ("polyurethane_topcoat", 2)],
        "total_dft_mils": 10,
        "service": "severe_industrial",
        "expected_life_years": 25,
    },
    "C2": {
        "layers": [("epoxy_primer", 4), ("epoxy_midcoat", 4), ("polyurethane_topcoat", 2)],
        "total_dft_mils": 10,
        "service": "moderate_industrial",
        "expected_life_years": 20,
    },
    "C3": {
        "layers": [("alkyd_primer", 2), ("alkyd_enamel", 2)],
        "total_dft_mils": 4,
        "service": "mild_interior",
        "expected_life_years": 10,
    },
    "HDG": {
        "layers": [("hot_dip_galvanizing", 3.5)],
        "total_dft_mils": 3.5,
        "service": "outdoor_structural",
        "expected_life_years": 50,
    },
    "DUPLEX": {
        "layers": [("hot_dip_galvanizing", 3.5), ("epoxy_primer", 2), ("polyurethane_topcoat", 2)],
        "total_dft_mils": 7.5,
        "service": "severe_marine",
        "expected_life_years": 75,
    },
}

# Galvanizing thickness requirements per ASTM A123
GALVANIZING_REQUIREMENTS = {
    # Material category: (min_thickness_mils, avg_thickness_mils)
    "structural_shapes": (3.9, 4.7),        # W, C, L shapes
    "plates_>3/16": (3.9, 4.7),
    "plates_1/8-3/16": (3.4, 4.2),
    "plates_<1/8": (2.7, 3.4),
    "pipe_conduit": (2.3, 2.8),
    "fasteners": (2.1, 2.6),
    "castings": (3.4, 4.2),
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class MaterialSpec:
    """Material specification data."""
    specification: str  # A36, A572-50, 304SS, etc.
    thickness: Optional[float] = None  # inches
    grade: Optional[str] = None
    heat_treatment: Optional[str] = None
    certification_required: bool = False
    mtr_required: bool = False  # Mill Test Report


@dataclass
class CoatingSpec:
    """Coating specification data."""
    coating_system: str  # C1, C2, HDG, etc.
    surface_prep: SurfacePrep = SurfacePrep.SP6
    primer: Optional[str] = None
    topcoat: Optional[str] = None
    total_dft_mils: Optional[float] = None
    service_environment: str = "moderate"


@dataclass
class MaterialsValidationResult:
    """Materials and finishing validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

    # Material issues
    material_compatible: bool = True
    weldability_ok: bool = True

    # Coating issues
    coating_adequate: bool = True
    prep_adequate: bool = True


# =============================================================================
# MATERIALS VALIDATOR
# =============================================================================

class MaterialsFinishingValidator:
    """
    Validates material specifications and surface finishing.

    Phase 25.6 - Checks:
    1. Material specification validity
    2. Material compatibility (dissimilar metals)
    3. Weldability requirements
    4. Coating system adequacy
    5. Surface preparation requirements
    6. Galvanizing thickness
    7. DFT requirements
    8. Service environment compatibility
    """

    def __init__(self):
        pass

    def validate_material(
        self,
        material: MaterialSpec,
        application: str = "structural"
    ) -> MaterialsValidationResult:
        """
        Validate material specification.

        Args:
            material: Material specification data
            application: "structural", "pressure", "cryogenic", etc.

        Returns:
            Validation result
        """
        result = MaterialsValidationResult()

        # Check 1: Valid specification
        result.total_checks += 1
        spec_upper = material.specification.upper().replace(" ", "")

        found = False
        for spec in STEEL_SPECIFICATIONS:
            if spec.upper().replace("-", "").replace(" ", "") in spec_upper:
                found = True
                break

        if not found:
            # Check stainless
            for grade in STAINLESS_GRADES:
                if grade in spec_upper:
                    found = True
                    break

        if not found:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="material_spec_unknown",
                message=f"Material specification '{material.specification}' not in standard database",
                suggestion="Verify specification is correct and add to material database",
            ))
            result.warnings += 1
        else:
            result.passed += 1

        # Check 2: Weldability
        result.total_checks += 1
        for spec, (yield_ksi, tensile_ksi, weldability, p_num) in STEEL_SPECIFICATIONS.items():
            if spec.upper().replace("-", "") in spec_upper.replace("-", ""):
                if weldability == "fair":
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        check_type="weldability_concern",
                        message=f"{spec} requires special welding procedures (P-Number {p_num})",
                        suggestion="Verify preheat, interpass temp, and PWHT requirements",
                        standard_reference="AWS D1.1 / ASME IX",
                    ))
                    result.warnings += 1
                    result.weldability_ok = False
                else:
                    result.passed += 1
                break
        else:
            result.passed += 1

        # Check 3: MTR requirement
        result.total_checks += 1
        if application in ["pressure", "cryogenic", "nuclear"]:
            if not material.mtr_required:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="mtr_required",
                    message=f"MTR (Mill Test Report) recommended for {application} application",
                    suggestion="Add MTR requirement to material specification",
                ))
                result.warnings += 1
            else:
                result.passed += 1
        else:
            result.passed += 1

        return result

    def check_material_compatibility(
        self,
        material_1: str,
        material_2: str
    ) -> MaterialsValidationResult:
        """
        Check galvanic compatibility of two materials.

        Args:
            material_1: First material specification
            material_2: Second material specification

        Returns:
            Validation result with compatibility info
        """
        result = MaterialsValidationResult()

        # Galvanic series (anodic to cathodic)
        galvanic_order = [
            "magnesium", "zinc", "galvanized", "aluminum", "cadmium",
            "carbon_steel", "cast_iron", "stainless_304", "stainless_316",
            "brass", "bronze", "copper", "nickel", "titanium"
        ]

        def get_galvanic_position(mat: str) -> int:
            mat_lower = mat.lower()
            if "magnesium" in mat_lower:
                return 0
            elif "galv" in mat_lower or "zinc" in mat_lower:
                return 1
            elif "alum" in mat_lower:
                return 3
            elif "316" in mat_lower:
                return 8
            elif "304" in mat_lower or "stainless" in mat_lower:
                return 7
            elif "brass" in mat_lower:
                return 9
            elif "bronze" in mat_lower:
                return 10
            elif "copper" in mat_lower:
                return 11
            elif "nickel" in mat_lower:
                return 12
            elif "titanium" in mat_lower:
                return 13
            else:  # Assume carbon steel
                return 5

        pos_1 = get_galvanic_position(material_1)
        pos_2 = get_galvanic_position(material_2)
        galvanic_difference = abs(pos_1 - pos_2)

        result.total_checks += 1

        if galvanic_difference >= 4:
            result.material_compatible = False
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                check_type="galvanic_incompatible",
                message=f"Galvanic corrosion risk: {material_1} + {material_2}",
                suggestion="Use insulating gaskets/bushings or select compatible materials",
            ))
            result.critical_failures += 1
            result.failed += 1
        elif galvanic_difference >= 2:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="galvanic_concern",
                message=f"Potential galvanic corrosion: {material_1} + {material_2}",
                suggestion="Consider protective coating at interface",
            ))
            result.warnings += 1
        else:
            result.passed += 1

        return result

    def validate_coating_system(
        self,
        coating: CoatingSpec,
        service_life_years: int = 20
    ) -> MaterialsValidationResult:
        """
        Validate coating system for service environment.

        Args:
            coating: Coating specification
            service_life_years: Required service life

        Returns:
            Validation result
        """
        result = MaterialsValidationResult()

        # Check 1: Valid coating system
        result.total_checks += 1
        system = COATING_SYSTEMS.get(coating.coating_system)

        if not system:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="coating_system_unknown",
                message=f"Coating system '{coating.coating_system}' not in standard database",
                suggestion="Specify coating layers and DFT explicitly",
            ))
            result.warnings += 1
        else:
            result.passed += 1

            # Check 2: Service life
            result.total_checks += 1
            if system.get("expected_life_years", 0) < service_life_years:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="coating_life_short",
                    message=f"Coating system life ({system['expected_life_years']}yr) < required ({service_life_years}yr)",
                    suggestion="Consider higher-performance coating system",
                ))
                result.warnings += 1
                result.coating_adequate = False
            else:
                result.passed += 1

        # Check 3: Surface prep adequacy
        result.total_checks += 1
        for coat_type, (min_prep, opt_prep, min_profile, max_profile) in COATING_PREP_REQUIREMENTS.items():
            if coating.primer and coat_type in coating.primer.lower():
                if coating.surface_prep.value < min_prep.value:
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        check_type="surface_prep_inadequate",
                        message=f"Surface prep {coating.surface_prep.name} inadequate for {coat_type}",
                        suggestion=f"Minimum prep: {min_prep.name}, optimal: {opt_prep.name}",
                        standard_reference="SSPC",
                    ))
                    result.prep_adequate = False
                    result.critical_failures += 1
                    result.failed += 1
                else:
                    result.passed += 1
                break
        else:
            result.passed += 1

        # Check 4: DFT specified
        result.total_checks += 1
        if coating.total_dft_mils is None:
            if system:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="dft_default",
                    message=f"Using system default DFT: {system['total_dft_mils']} mils",
                ))
            else:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="dft_missing",
                    message="Dry Film Thickness (DFT) not specified",
                    suggestion="Specify total DFT requirement",
                ))
                result.warnings += 1
        result.passed += 1

        return result

    def validate_galvanizing(
        self,
        material_category: str,
        measured_thickness_mils: Optional[float] = None
    ) -> MaterialsValidationResult:
        """
        Validate hot-dip galvanizing per ASTM A123.

        Args:
            material_category: "structural_shapes", "plates_>3/16", etc.
            measured_thickness_mils: Measured coating thickness

        Returns:
            Validation result
        """
        result = MaterialsValidationResult()

        requirements = GALVANIZING_REQUIREMENTS.get(material_category)

        result.total_checks += 1
        if not requirements:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="galv_category_unknown",
                message=f"Category '{material_category}' not in ASTM A123 table",
                suggestion="Verify material category for galvanizing requirements",
            ))
            result.passed += 1
            return result

        min_thick, avg_thick = requirements

        if measured_thickness_mils is not None:
            result.total_checks += 1
            if measured_thickness_mils < min_thick:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    check_type="galv_thickness_low",
                    message=f"Galvanizing {measured_thickness_mils} mils < min {min_thick} mils",
                    suggestion="Reject or re-galvanize",
                    standard_reference="ASTM A123",
                ))
                result.critical_failures += 1
                result.failed += 1
            else:
                result.passed += 1
        else:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="galv_requirement",
                message=f"Galvanizing requirement: min {min_thick} mils, avg {avg_thick} mils",
                standard_reference="ASTM A123",
            ))
            result.passed += 1

        return result

    def to_dict(self, result: MaterialsValidationResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "materials_finishing",
            "total_checks": result.total_checks,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "critical_failures": result.critical_failures,
            "material_compatible": result.material_compatible,
            "weldability_ok": result.weldability_ok,
            "coating_adequate": result.coating_adequate,
            "prep_adequate": result.prep_adequate,
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
