"""
SSPC Surface Preparation Validator
===================================
Validates coating and surface preparation specifications per SSPC/NACE standards.

Phase 25 - ACHE Standards Compliance
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.sspc_coating")


class SurfacePrep(str, Enum):
    """SSPC Surface Preparation Standards."""
    SP1 = "SP-1"     # Solvent Cleaning
    SP2 = "SP-2"     # Hand Tool Cleaning
    SP3 = "SP-3"     # Power Tool Cleaning
    SP6 = "SP-6"     # Commercial Blast Cleaning
    SP7 = "SP-7"     # Brush-Off Blast Cleaning
    SP10 = "SP-10"   # Near-White Blast Cleaning
    SP5 = "SP-5"     # White Metal Blast Cleaning
    SP11 = "SP-11"   # Power Tool Cleaning to Bare Metal
    SP14 = "SP-14"   # Industrial Blast Cleaning
    SP15 = "SP-15"   # Commercial Grade Power Tool Cleaning
    SP16 = "SP-16"   # Brush-Off Blast for Coated/Uncoated Surfaces


# SSPC/NACE equivalent standards
SSPC_NACE_EQUIVALENTS = {
    "SP-1": "NACE No. 1",
    "SP-2": "NACE No. 4",
    "SP-3": "NACE No. 4",
    "SP-5": "NACE No. 1",
    "SP-6": "NACE No. 3",
    "SP-7": "NACE No. 4",
    "SP-10": "NACE No. 2",
}

# ISO 8501 equivalents (Sa grades for blast, St for tool)
SSPC_ISO_EQUIVALENTS = {
    "SP-5": "Sa 3",       # White Metal
    "SP-10": "Sa 2.5",    # Near-White
    "SP-6": "Sa 2",       # Commercial
    "SP-7": "Sa 1",       # Brush-Off
    "SP-2": "St 2",       # Hand Tool
    "SP-3": "St 3",       # Power Tool
}

# Minimum surface prep by environment/coating type
ENVIRONMENT_PREP_REQUIREMENTS = {
    "immersion": "SP-5",      # Tanks, submerged
    "marine": "SP-10",        # Offshore, coastal
    "industrial_severe": "SP-10",
    "industrial_moderate": "SP-6",
    "rural_mild": "SP-6",
    "interior_dry": "SP-3",
}

# Typical DFT (dry film thickness) ranges by coating type (mils)
COATING_DFT_RANGES = {
    "primer": {"min": 1.0, "max": 3.0, "typical": 2.0},
    "epoxy": {"min": 4.0, "max": 10.0, "typical": 6.0},
    "epoxy_primer": {"min": 2.0, "max": 4.0, "typical": 3.0},
    "urethane": {"min": 2.0, "max": 4.0, "typical": 3.0},
    "polyurethane": {"min": 2.0, "max": 4.0, "typical": 3.0},
    "zinc_rich": {"min": 2.5, "max": 4.0, "typical": 3.0},
    "inorganic_zinc": {"min": 2.5, "max": 4.0, "typical": 3.0},
    "alkyd": {"min": 1.5, "max": 3.0, "typical": 2.0},
    "phenolic": {"min": 4.0, "max": 8.0, "typical": 6.0},
    "coal_tar_epoxy": {"min": 8.0, "max": 16.0, "typical": 12.0},
}


@dataclass
class CoatingSpec:
    """Coating specification data."""
    surface_prep: Optional[str] = None
    primer_type: Optional[str] = None
    primer_dft_mils: Optional[float] = None
    intermediate_type: Optional[str] = None
    intermediate_dft_mils: Optional[float] = None
    topcoat_type: Optional[str] = None
    topcoat_dft_mils: Optional[float] = None
    total_dft_mils: Optional[float] = None
    environment: Optional[str] = None  # immersion, marine, industrial, etc.
    substrate: str = "carbon_steel"


@dataclass
class SSPCValidationResult:
    """SSPC coating validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

    # Statistics
    surface_prep_validated: bool = False
    dft_validated: bool = False
    system_validated: bool = False


class SSPCCoatingValidator:
    """
    Validates coating specifications per SSPC standards.

    Checks:
    1. Surface prep standard validity (SP-1 through SP-16)
    2. Surface prep appropriate for environment
    3. Primer DFT within range
    4. Total system DFT adequate
    5. Coating system compatibility
    6. NACE/ISO equivalent callout
    """

    def __init__(self):
        pass

    def validate_coating(self, spec: CoatingSpec) -> SSPCValidationResult:
        """
        Validate coating specification.

        Args:
            spec: Coating specification data

        Returns:
            Validation result
        """
        result = SSPCValidationResult()

        self._check_surface_prep_validity(spec, result)
        self._check_surface_prep_for_environment(spec, result)
        self._check_primer_dft(spec, result)
        self._check_total_dft(spec, result)
        self._check_coating_compatibility(spec, result)
        self._check_equivalent_standards(spec, result)

        return result

    def _check_surface_prep_validity(self, spec: CoatingSpec, result: SSPCValidationResult):
        """Check if surface prep standard is valid SSPC specification."""
        result.total_checks += 1

        if not spec.surface_prep:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="surface_prep_missing",
                message="Surface preparation standard not specified",
                suggestion="Specify SSPC surface prep (e.g., SP-6, SP-10, SP-5)",
                standard_reference="SSPC",
            ))
            return

        # Normalize input
        prep = spec.surface_prep.upper().replace(" ", "").replace("-", "-")
        if not prep.startswith("SP-"):
            prep = f"SP-{prep.replace('SP', '')}"

        # Check if valid
        valid_preps = [e.value for e in SurfacePrep]
        if prep not in valid_preps:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="surface_prep_invalid",
                message=f"Surface prep '{spec.surface_prep}' is not a valid SSPC standard",
                suggestion=f"Use valid SSPC standard: {', '.join(valid_preps[:6])}...",
                standard_reference="SSPC",
            ))
        else:
            result.passed += 1
            result.surface_prep_validated = True

    def _check_surface_prep_for_environment(self, spec: CoatingSpec, result: SSPCValidationResult):
        """Check if surface prep is adequate for service environment."""
        result.total_checks += 1

        if not spec.surface_prep or not spec.environment:
            return

        prep = spec.surface_prep.upper().replace(" ", "")
        if not prep.startswith("SP-"):
            prep = f"SP-{prep.replace('SP', '')}"

        env = spec.environment.lower().replace(" ", "_")

        if env in ENVIRONMENT_PREP_REQUIREMENTS:
            required = ENVIRONMENT_PREP_REQUIREMENTS[env]

            # Define prep hierarchy (higher = better)
            prep_hierarchy = {
                "SP-1": 1, "SP-2": 2, "SP-3": 3, "SP-7": 4,
                "SP-14": 5, "SP-6": 6, "SP-10": 7, "SP-5": 8,
            }

            req_level = prep_hierarchy.get(required, 0)
            actual_level = prep_hierarchy.get(prep, 0)

            if actual_level < req_level:
                result.failed += 1
                result.critical_failures += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    check_type="surface_prep_inadequate",
                    message=f"Surface prep {prep} inadequate for {env} environment",
                    suggestion=f"Use minimum {required} for {env} service",
                    standard_reference="SSPC/NACE",
                ))
            else:
                result.passed += 1

    def _check_primer_dft(self, spec: CoatingSpec, result: SSPCValidationResult):
        """Check primer DFT is within acceptable range."""
        result.total_checks += 1

        if not spec.primer_dft_mils:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="primer_dft_missing",
                message="Primer DFT not specified",
                suggestion="Specify primer dry film thickness in mils",
            ))
            return

        primer_type = (spec.primer_type or "primer").lower().replace(" ", "_")

        if primer_type in COATING_DFT_RANGES:
            ranges = COATING_DFT_RANGES[primer_type]

            if spec.primer_dft_mils < ranges["min"]:
                result.failed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="primer_dft_low",
                    message=f"Primer DFT {spec.primer_dft_mils} mils below minimum {ranges['min']} mils",
                    suggestion=f"Increase primer DFT to ≥{ranges['min']} mils",
                ))
            elif spec.primer_dft_mils > ranges["max"]:
                result.warnings += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="primer_dft_high",
                    message=f"Primer DFT {spec.primer_dft_mils} mils exceeds typical max {ranges['max']} mils",
                    suggestion=f"Verify DFT requirement (typical: {ranges['typical']} mils)",
                ))
            else:
                result.passed += 1
                result.dft_validated = True

    def _check_total_dft(self, spec: CoatingSpec, result: SSPCValidationResult):
        """Check total system DFT is adequate."""
        result.total_checks += 1

        # Calculate or use provided total
        total_dft = spec.total_dft_mils
        if total_dft is None:
            total_dft = 0
            if spec.primer_dft_mils:
                total_dft += spec.primer_dft_mils
            if spec.intermediate_dft_mils:
                total_dft += spec.intermediate_dft_mils
            if spec.topcoat_dft_mils:
                total_dft += spec.topcoat_dft_mils

        if total_dft == 0:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="total_dft_missing",
                message="Total coating DFT not determinable",
                suggestion="Specify coat DFT values or total system DFT",
            ))
            return

        # Check minimum for environment
        env = (spec.environment or "").lower()
        min_dft = 4.0  # Default minimum

        if "immersion" in env or "marine" in env:
            min_dft = 12.0
        elif "industrial" in env and "severe" in env:
            min_dft = 10.0
        elif "industrial" in env:
            min_dft = 6.0

        if total_dft < min_dft:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="total_dft_inadequate",
                message=f"Total DFT {total_dft} mils may be inadequate for {spec.environment or 'service'}",
                suggestion=f"Consider minimum {min_dft} mils total system DFT",
            ))
        else:
            result.passed += 1
            result.system_validated = True

    def _check_coating_compatibility(self, spec: CoatingSpec, result: SSPCValidationResult):
        """Check coating system compatibility."""
        result.total_checks += 1

        primer = (spec.primer_type or "").lower()
        topcoat = (spec.topcoat_type or "").lower()

        # Known incompatibilities
        incompatible = []

        # Zinc-rich primers with certain topcoats
        if "zinc" in primer and "alkyd" in topcoat:
            incompatible.append(("Zinc-rich primer", "alkyd topcoat", "Use epoxy or urethane topcoat over zinc"))

        # Coal tar with urethane
        if "coal tar" in primer and "urethane" in topcoat:
            incompatible.append(("Coal tar", "urethane", "Use epoxy or phenolic topcoat"))

        if incompatible:
            for p, t, fix in incompatible:
                result.failed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="coating_incompatible",
                    message=f"Incompatible coating system: {p} with {t}",
                    suggestion=fix,
                ))
        else:
            result.passed += 1

    def _check_equivalent_standards(self, spec: CoatingSpec, result: SSPCValidationResult):
        """Check for NACE/ISO equivalent callout."""
        result.total_checks += 1

        if not spec.surface_prep:
            return

        prep = spec.surface_prep.upper()
        if not prep.startswith("SP-"):
            prep = f"SP-{prep.replace('SP', '').replace('-', '')}"

        # Add info about equivalents
        nace_eq = SSPC_NACE_EQUIVALENTS.get(prep)
        iso_eq = SSPC_ISO_EQUIVALENTS.get(prep)

        if nace_eq or iso_eq:
            equiv_str = []
            if nace_eq:
                equiv_str.append(nace_eq)
            if iso_eq:
                equiv_str.append(f"ISO 8501-1 {iso_eq}")

            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="equivalent_standards",
                message=f"{prep} equivalent: {', '.join(equiv_str)}",
                suggestion="Consider adding equivalent callout for international projects",
            ))

        result.passed += 1

    def get_prep_description(self, prep: str) -> Optional[str]:
        """Get description of surface prep standard."""
        descriptions = {
            "SP-1": "Solvent Cleaning - Remove oil, grease, dirt",
            "SP-2": "Hand Tool Cleaning - Remove loose mill scale, rust, paint",
            "SP-3": "Power Tool Cleaning - Remove loose scale, rust to bare metal",
            "SP-5": "White Metal Blast - Remove all visible rust, scale, paint",
            "SP-6": "Commercial Blast - 2/3 of surface free of visible residue",
            "SP-7": "Brush-Off Blast - Remove loose material only",
            "SP-10": "Near-White Blast - 95% free of visible residue",
            "SP-11": "Power Tool Cleaning to Bare Metal",
        }
        return descriptions.get(prep.upper())

    def to_dict(self, result: SSPCValidationResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "sspc_coating",
            "total_checks": result.total_checks,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "critical_failures": result.critical_failures,
            "statistics": {
                "surface_prep_validated": result.surface_prep_validated,
                "dft_validated": result.dft_validated,
                "system_validated": result.system_validated,
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
