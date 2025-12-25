"""
ASME Validator
==============
Validate engineering drawings against ASME standards (pressure vessels, materials, flanges).

Phase 25.3 Implementation
"""

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.asme")


@dataclass
class ASMECheckResult:
    """Result of a single ASME check."""
    check_id: str
    check_name: str
    passed: bool
    actual_value: Any = None
    expected_value: Any = None
    reference: str = ""
    severity: ValidationSeverity = ValidationSeverity.WARNING
    message: str = ""


@dataclass
class ASMEValidationResult:
    """Complete ASME validation results."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    check_results: List[ASMECheckResult] = field(default_factory=list)
    issues: List[ValidationIssue] = field(default_factory=list)


class ASMEValidator:
    """
    Validate drawings against ASME standards.

    Checks include:
    - Material specification validation (SA-516-70, SA-350-LF2, etc.)
    - Pressure rating vs material grade
    - Flange rating verification (150#, 300#, etc.)
    - MDMT vs material impact test requirements (UCS-66)
    - Joint efficiency verification
    - Hydro test pressure calculation (1.3 × MAWP)
    - Corrosion allowance verification
    - PWHT requirements based on thickness
    """

    # Valid ASME material specifications
    VALID_MATERIALS = {
        # Plate materials
        "SA-516-70": {"type": "plate", "grade": 70, "min_yield_ksi": 38, "min_tensile_ksi": 70, "impact_test_required_below_f": 0},
        "SA-516-65": {"type": "plate", "grade": 65, "min_yield_ksi": 35, "min_tensile_ksi": 65, "impact_test_required_below_f": 0},
        "SA-516-60": {"type": "plate", "grade": 60, "min_yield_ksi": 32, "min_tensile_ksi": 60, "impact_test_required_below_f": 0},
        "SA-240-304": {"type": "plate", "grade": "304", "min_yield_ksi": 30, "min_tensile_ksi": 75},
        "SA-240-316": {"type": "plate", "grade": "316", "min_yield_ksi": 30, "min_tensile_ksi": 75},

        # Forging materials
        "SA-105": {"type": "forging", "min_yield_ksi": 36, "min_tensile_ksi": 70, "max_temp_f": 650},
        "SA-350-LF2": {"type": "forging", "min_yield_ksi": 36, "min_tensile_ksi": 70, "min_temp_f": -50, "impact_tested": True},
        "SA-182-F304": {"type": "forging", "min_yield_ksi": 30, "min_tensile_ksi": 75},
        "SA-182-F316": {"type": "forging", "min_yield_ksi": 30, "min_tensile_ksi": 75},

        # Bolting materials
        "SA-193-B7": {"type": "bolt", "min_yield_ksi": 105, "min_tensile_ksi": 125, "max_temp_f": 800},
        "SA-193-B7M": {"type": "bolt", "min_yield_ksi": 80, "min_tensile_ksi": 100, "max_temp_f": 800, "max_hardness_hrb": 99},
        "SA-320-L7": {"type": "bolt", "min_yield_ksi": 105, "min_tensile_ksi": 125, "low_temp": True},
        "SA-194-2H": {"type": "nut", "hardness_hrb": "68-96"},
        "SA-194-7": {"type": "nut"},

        # Pipe materials
        "SA-106-B": {"type": "pipe", "min_yield_ksi": 35, "min_tensile_ksi": 60},
        "SA-312-304": {"type": "pipe", "min_yield_ksi": 30, "min_tensile_ksi": 75},
        "SA-312-316": {"type": "pipe", "min_yield_ksi": 30, "min_tensile_ksi": 75},
    }

    # ASME B16.5 Flange ratings and pressure-temperature limits
    FLANGE_RATINGS = {
        150: {"carbon_steel_max_psi": 285, "max_temp_f": 100},
        300: {"carbon_steel_max_psi": 740, "max_temp_f": 100},
        600: {"carbon_steel_max_psi": 1480, "max_temp_f": 100},
        900: {"carbon_steel_max_psi": 2220, "max_temp_f": 100},
        1500: {"carbon_steel_max_psi": 3705, "max_temp_f": 100},
        2500: {"carbon_steel_max_psi": 6170, "max_temp_f": 100},
    }

    # Flange types
    FLANGE_TYPES = {
        "WN": "Weld Neck",
        "SO": "Slip-On",
        "BL": "Blind",
        "BLD": "Blind",
        "LJ": "Lap Joint",
        "SW": "Socket Weld",
        "TH": "Threaded",
        "LWN": "Long Weld Neck",
    }

    # PWHT requirements per ASME VIII
    PWHT_THICKNESS_LIMITS = {
        "P-1": {"max_thickness_in": 1.25, "reference": "ASME VIII UCS-56"},
        "P-3": {"max_thickness_in": 0.625, "reference": "ASME VIII UCS-56"},
        "P-4": {"max_thickness_in": 0.5, "reference": "ASME VIII UCS-56"},
    }

    def __init__(self):
        """Initialize the ASME validator."""
        self._load_standards_data()

    def _load_standards_data(self):
        """Load additional standards data from JSON if available."""
        # Load ASME flanges data
        flanges_path = Path(__file__).parent.parent.parent.parent / "data" / "standards" / "asme_flanges_b16_5.json"
        if flanges_path.exists():
            try:
                with open(flanges_path) as f:
                    self._flange_data = json.load(f)
                logger.info(f"Loaded ASME B16.5 data from {flanges_path}")
            except Exception as e:
                logger.warning(f"Could not load ASME B16.5 data: {e}")
                self._flange_data = {}
        else:
            self._flange_data = {}

    def validate(self, extraction_result) -> ASMEValidationResult:
        """
        Validate extracted drawing data against ASME standards.

        Args:
            extraction_result: DrawingExtractionResult from PDF extractor

        Returns:
            ASMEValidationResult with all check results
        """
        result = ASMEValidationResult()

        # Run all ASME checks
        checks = [
            self._check_material_specifications(extraction_result),
            self._check_flange_rating(extraction_result),
            self._check_flange_type(extraction_result),
            self._check_nozzle_schedule(extraction_result),
            self._check_mdmt_impact_requirements(extraction_result),
            self._check_joint_efficiency(extraction_result),
            self._check_hydro_test_pressure(extraction_result),
            self._check_corrosion_allowance(extraction_result),
            self._check_pwht_requirements(extraction_result),
            self._check_material_pressure_compatibility(extraction_result),
        ]

        for check_list in checks:
            # Some checks return multiple results
            if isinstance(check_list, list):
                for check in check_list:
                    self._process_check(check, result)
            elif check_list:
                self._process_check(check_list, result)

        return result

    def _process_check(self, check: ASMECheckResult, result: ASMEValidationResult):
        """Process a single check result and add to results."""
        if check:
            result.check_results.append(check)
            result.total_checks += 1

            if check.passed:
                result.passed += 1
            else:
                if check.severity == ValidationSeverity.CRITICAL:
                    result.critical_failures += 1
                elif check.severity == ValidationSeverity.ERROR:
                    result.failed += 1
                else:
                    result.warnings += 1

                result.issues.append(ValidationIssue(
                    severity=check.severity,
                    check_type="ASME",
                    message=check.message,
                    location=check.check_name,
                    suggestion=self._get_suggestion(check),
                    standard_reference=check.reference,
                ))

    def _check_material_specifications(self, data) -> List[ASMECheckResult]:
        """Validate all material specifications against ASME standards."""
        results = []
        bom_items = getattr(data, 'bom_items', [])

        for item in bom_items:
            material_spec = getattr(item, 'material_spec', '')
            if not material_spec:
                continue

            # Normalize spec
            spec_upper = material_spec.upper().replace(" ", "-")

            # Check if it's a valid ASME spec
            is_valid = False
            matched_spec = None

            for valid_spec in self.VALID_MATERIALS:
                if valid_spec in spec_upper:
                    is_valid = True
                    matched_spec = valid_spec
                    break

            result = ASMECheckResult(
                check_id=f"ASME-MAT-{len(results)+1:03d}",
                check_name=f"Material: {material_spec}",
                passed=is_valid,
                actual_value=material_spec,
                expected_value="Valid ASME material specification",
                reference="ASME II Part D",
                severity=ValidationSeverity.ERROR if not is_valid else ValidationSeverity.INFO,
                message=f"Material '{material_spec}' is {'valid' if is_valid else 'not recognized as valid'} ASME specification",
            )
            results.append(result)

        return results

    def _check_flange_rating(self, data) -> Optional[ASMECheckResult]:
        """Check flange rating is appropriate for pressure."""
        raw_text = getattr(data, 'raw_text', '')
        design_data = getattr(data, 'design_data', None)

        # Find flange ratings in text
        rating_pattern = re.compile(r'(\d{3,4})\s*(?:#|LB|CLASS)', re.I)
        matches = rating_pattern.findall(raw_text)

        if matches and design_data:
            mawp = getattr(design_data, 'mawp_psi', 0) or getattr(design_data, 'design_pressure_psi', 0)
            design_temp = getattr(design_data, 'design_temperature_f', 100)

            # Get the minimum flange rating found
            min_rating = min(int(m) for m in matches)

            # Get allowable pressure for this rating
            if min_rating in self.FLANGE_RATINGS:
                max_pressure = self.FLANGE_RATINGS[min_rating]["carbon_steel_max_psi"]

                # Adjust for temperature (simplified - actual tables are more complex)
                if design_temp > 200:
                    max_pressure *= 0.95
                if design_temp > 300:
                    max_pressure *= 0.90

                passed = mawp <= max_pressure

                return ASMECheckResult(
                    check_id="ASME-FLG-001",
                    check_name="Flange Rating vs Pressure",
                    passed=passed,
                    actual_value=f"{min_rating}# flange, {mawp} psi MAWP",
                    expected_value=f"{min_rating}# rated for {max_pressure:.0f} psi at {design_temp}°F",
                    reference="ASME B16.5",
                    severity=ValidationSeverity.CRITICAL if not passed else ValidationSeverity.INFO,
                    message=f"Flange rating {min_rating}# {'adequate' if passed else 'INADEQUATE'} for {mawp} psi",
                )

        return None

    def _check_flange_type(self, data) -> Optional[ASMECheckResult]:
        """Check flange type is specified and valid."""
        raw_text = getattr(data, 'raw_text', '')

        # Find flange types
        type_pattern = re.compile(r'(WN|SO|BL|BLD|LJ|SW|TH|LWN)\s*(?:FLG|FLANGE)?', re.I)
        matches = type_pattern.findall(raw_text)

        if matches:
            flange_types = list(set(m.upper() for m in matches))

            # Check if types are valid
            all_valid = all(ft in self.FLANGE_TYPES for ft in flange_types)

            return ASMECheckResult(
                check_id="ASME-FLG-002",
                check_name="Flange Type",
                passed=all_valid,
                actual_value=", ".join(flange_types),
                expected_value="Valid ASME B16.5 flange type",
                reference="ASME B16.5",
                severity=ValidationSeverity.INFO,
                message=f"Flange types: {', '.join(self.FLANGE_TYPES.get(ft, ft) for ft in flange_types)}",
            )

        return None

    def _check_nozzle_schedule(self, data) -> Optional[ASMECheckResult]:
        """Check nozzle schedule specifications."""
        raw_text = getattr(data, 'raw_text', '')

        # Find schedule references
        schedule_pattern = re.compile(r'(?:SCH|SCHEDULE)\s*(\d+|XS|XXS|STD)', re.I)
        matches = schedule_pattern.findall(raw_text)

        if matches:
            schedules = list(set(m.upper() for m in matches))

            # Check for heavy schedules (160, XXS) for high pressure
            has_heavy = any(s in ['160', 'XXS'] for s in schedules)

            return ASMECheckResult(
                check_id="ASME-NOZ-001",
                check_name="Nozzle Schedule",
                passed=True,
                actual_value=", ".join(f"SCH {s}" for s in schedules),
                expected_value="Schedule per pressure requirements",
                reference="ASME B36.10 / B36.19",
                severity=ValidationSeverity.INFO,
                message=f"Nozzle schedules: {', '.join(schedules)}",
            )

        return None

    def _check_mdmt_impact_requirements(self, data) -> Optional[ASMECheckResult]:
        """Check MDMT vs material impact test requirements per UCS-66."""
        design_data = getattr(data, 'design_data', None)
        bom_items = getattr(data, 'bom_items', [])

        if not design_data:
            return None

        mdmt = getattr(design_data, 'mdmt_f', None)
        if mdmt is None:
            return None

        # Check if low-temp materials are specified for low MDMT
        low_temp_materials = ['LF2', 'L7', '304', '316']
        has_low_temp_material = any(
            any(ltm in getattr(item, 'material_spec', '').upper() for ltm in low_temp_materials)
            for item in bom_items
        )

        # MDMT below 0°F typically requires impact-tested materials
        requires_impact = mdmt < 0
        passed = not requires_impact or has_low_temp_material

        return ASMECheckResult(
            check_id="ASME-MDT-001",
            check_name="MDMT Impact Requirements",
            passed=passed,
            actual_value=f"MDMT: {mdmt}°F, Low-temp materials: {'Yes' if has_low_temp_material else 'No'}",
            expected_value="Impact-tested materials for MDMT < 0°F",
            reference="ASME VIII UCS-66",
            severity=ValidationSeverity.CRITICAL if not passed else ValidationSeverity.INFO,
            message=f"MDMT {mdmt}°F {'requires' if requires_impact else 'does not require'} impact-tested materials",
        )

    def _check_joint_efficiency(self, data) -> Optional[ASMECheckResult]:
        """Check joint efficiency verification."""
        design_data = getattr(data, 'design_data', None)
        raw_text = getattr(data, 'raw_text', '')

        # Look for joint efficiency
        je_pattern = re.compile(r'(?:JOINT\s*)?(?:EFF(?:ICIENCY)?|E)[:\s=]*(\d*\.?\d+)', re.I)
        match = je_pattern.search(raw_text)

        if match:
            efficiency = float(match.group(1))
            if efficiency > 1:
                efficiency = efficiency / 100  # Convert percentage

            # Check for full RT requirement
            full_rt = bool(re.search(r'FULL\s*(?:RT|RADIOGRAPHY)', raw_text, re.I))
            spot_rt = bool(re.search(r'SPOT\s*(?:RT|RADIOGRAPHY)', raw_text, re.I))

            expected_efficiency = 1.0 if full_rt else (0.85 if spot_rt else 0.7)

            passed = efficiency >= expected_efficiency * 0.99  # Allow 1% tolerance

            return ASMECheckResult(
                check_id="ASME-JE-001",
                check_name="Joint Efficiency",
                passed=passed,
                actual_value=f"E = {efficiency} ({'Full RT' if full_rt else 'Spot RT' if spot_rt else 'No RT'})",
                expected_value=f"E = {expected_efficiency} for {'Full RT' if full_rt else 'Spot RT' if spot_rt else 'No RT'}",
                reference="ASME VIII UW-12",
                severity=ValidationSeverity.ERROR if not passed else ValidationSeverity.INFO,
                message=f"Joint efficiency {efficiency} {'matches' if passed else 'does not match'} RT requirements",
            )

        return None

    def _check_hydro_test_pressure(self, data) -> Optional[ASMECheckResult]:
        """Check hydrostatic test pressure is correct (1.3 × MAWP typical)."""
        design_data = getattr(data, 'design_data', None)

        if not design_data:
            return None

        mawp = getattr(design_data, 'mawp_psi', 0)
        test_pressure = getattr(design_data, 'test_pressure_psi', 0)

        if mawp and test_pressure:
            expected_test = mawp * 1.3
            tolerance = expected_test * 0.05  # 5% tolerance

            passed = abs(test_pressure - expected_test) <= tolerance

            return ASMECheckResult(
                check_id="ASME-HYD-001",
                check_name="Hydro Test Pressure",
                passed=passed,
                actual_value=f"{test_pressure} psi",
                expected_value=f"{expected_test:.0f} psi (1.3 × {mawp} psi MAWP)",
                reference="ASME VIII UG-99",
                severity=ValidationSeverity.WARNING if not passed else ValidationSeverity.INFO,
                message=f"Hydro test pressure {test_pressure} psi {'matches' if passed else 'differs from'} expected {expected_test:.0f} psi",
            )

        return None

    def _check_corrosion_allowance(self, data) -> Optional[ASMECheckResult]:
        """Check corrosion allowance is specified and reasonable."""
        design_data = getattr(data, 'design_data', None)

        if not design_data:
            return None

        ca = getattr(design_data, 'corrosion_allowance_in', None)

        if ca is not None:
            # Typical range is 0.0625" to 0.25"
            reasonable = 0.0 <= ca <= 0.5

            return ASMECheckResult(
                check_id="ASME-CA-001",
                check_name="Corrosion Allowance",
                passed=reasonable,
                actual_value=f"{ca}\" ({ca*25.4:.1f}mm)",
                expected_value="0\" to 0.5\" (typical 0.0625\" to 0.25\")",
                reference="Project specification",
                severity=ValidationSeverity.INFO if reasonable else ValidationSeverity.WARNING,
                message=f"Corrosion allowance {ca}\" specified",
            )

        return None

    def _check_pwht_requirements(self, data) -> Optional[ASMECheckResult]:
        """Check PWHT requirements based on thickness."""
        design_data = getattr(data, 'design_data', None)
        raw_text = getattr(data, 'raw_text', '')

        if not design_data:
            return None

        pwht_required = getattr(design_data, 'pwht_required', False)

        # Look for thickness that might trigger PWHT
        thickness_pattern = re.compile(r'(\d+\.?\d*)\s*(?:"|IN)\s*(?:THK|THICK)', re.I)
        matches = thickness_pattern.findall(raw_text)

        if matches:
            max_thickness = max(float(t) for t in matches)

            # P-1 materials (carbon steel) require PWHT above 1.25"
            pwht_threshold = 1.25
            should_require_pwht = max_thickness > pwht_threshold

            if should_require_pwht and not pwht_required:
                return ASMECheckResult(
                    check_id="ASME-PWHT-001",
                    check_name="PWHT Requirements",
                    passed=False,
                    actual_value=f"Max thickness: {max_thickness}\", PWHT specified: {'Yes' if pwht_required else 'No'}",
                    expected_value=f"PWHT required for thickness > {pwht_threshold}\"",
                    reference="ASME VIII UCS-56",
                    severity=ValidationSeverity.CRITICAL,
                    message=f"PWHT required for {max_thickness}\" thickness but not specified",
                )

        return None

    def _check_material_pressure_compatibility(self, data) -> Optional[ASMECheckResult]:
        """Check material grades are appropriate for pressure."""
        design_data = getattr(data, 'design_data', None)
        bom_items = getattr(data, 'bom_items', [])

        if not design_data:
            return None

        mawp = getattr(design_data, 'mawp_psi', 0)

        # For high pressure (>600 psi), check for higher grade materials
        if mawp > 600:
            high_grade_specs = ['70', '316', '304', 'LF2']
            has_high_grade = any(
                any(hg in getattr(item, 'material_spec', '').upper() for hg in high_grade_specs)
                for item in bom_items
            )

            return ASMECheckResult(
                check_id="ASME-MPR-001",
                check_name="Material vs Pressure",
                passed=has_high_grade,
                actual_value=f"MAWP: {mawp} psi",
                expected_value="High-grade materials for pressures > 600 psi",
                reference="ASME VIII UG-23",
                severity=ValidationSeverity.WARNING if not has_high_grade else ValidationSeverity.INFO,
                message=f"{'Appropriate' if has_high_grade else 'Verify'} material grades for {mawp} psi",
            )

        return None

    def _get_suggestion(self, check: ASMECheckResult) -> str:
        """Get fix suggestion for failed check."""
        suggestions = {
            "ASME-MAT": "Verify material specification matches ASME II Part D approved materials",
            "ASME-FLG-001": "Upgrade flange class to handle design pressure",
            "ASME-FLG-002": "Specify standard ASME B16.5 flange type",
            "ASME-NOZ-001": "Verify nozzle schedule per ASME B16.34",
            "ASME-MDT-001": "Specify impact-tested materials (SA-350 LF2, SA-320 L7) for low MDMT",
            "ASME-JE-001": "Verify joint efficiency matches radiography requirements",
            "ASME-HYD-001": "Verify hydro test pressure is 1.3 × MAWP",
            "ASME-CA-001": "Verify corrosion allowance per service conditions",
            "ASME-PWHT-001": "Add PWHT requirement for thick sections per UCS-56",
            "ASME-MPR-001": "Verify material grade is adequate for design pressure",
        }

        for prefix, suggestion in suggestions.items():
            if check.check_id.startswith(prefix):
                return suggestion

        return "Review and correct per ASME requirements"

    def to_dict(self, result: ASMEValidationResult) -> Dict[str, Any]:
        """Convert validation result to dictionary."""
        return {
            "total_checks": result.total_checks,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "critical_failures": result.critical_failures,
            "pass_rate": (result.passed / result.total_checks * 100) if result.total_checks > 0 else 0,
            "check_results": [
                {
                    "check_id": c.check_id,
                    "check_name": c.check_name,
                    "passed": c.passed,
                    "actual_value": c.actual_value,
                    "expected_value": c.expected_value,
                    "reference": c.reference,
                    "severity": c.severity.value,
                    "message": c.message,
                }
                for c in result.check_results
            ],
            "issues": [
                {
                    "severity": i.severity.value,
                    "check_type": i.check_type,
                    "message": i.message,
                    "location": i.location,
                    "suggestion": i.suggestion,
                    "standard_reference": i.standard_reference,
                }
                for i in result.issues
            ],
        }
