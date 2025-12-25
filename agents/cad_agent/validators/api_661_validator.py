"""
API 661 Validator
=================
Validate engineering drawings against API 661 (Air-Cooled Heat Exchangers) standards.

Phase 25.2 Implementation
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.api_661")


@dataclass
class API661CheckResult:
    """Result of a single API 661 check."""
    check_id: str
    check_name: str
    passed: bool
    actual_value: Any = None
    expected_value: Any = None
    tolerance: Any = None
    reference: str = ""
    severity: ValidationSeverity = ValidationSeverity.WARNING
    message: str = ""


@dataclass
class API661ValidationResult:
    """Complete API 661 validation results."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    check_results: List[API661CheckResult] = field(default_factory=list)
    issues: List[ValidationIssue] = field(default_factory=list)


class API661Validator:
    """
    Validate drawings against API 661 standards for Air-Cooled Heat Exchangers.

    Checks include:
    - Tube pitch verification (2.75" typical)
    - Tube support spacing (max 1.83m / 6ft)
    - Tube bundle lateral movement (min 6mm each direction)
    - Header type for pressure rating
    - Plug hardness (HRB 68 max CS, HRB 82 max SS)
    - Fin strip back dimensions
    - Fan coverage ratio (min 40%)
    - Plenum depth (min 915mm / 36")
    """

    # API 661 Standards Data
    STANDARDS = {
        "tube_pitch": {
            "standard_in": 2.75,
            "tolerance_in": 0.03,
            "reference": "API 661 Table 2",
        },
        "tube_support_spacing": {
            "max_mm": 1830,
            "max_ft": 6,
            "reference": "API 661 para 4.1.7",
        },
        "bundle_lateral_movement": {
            "min_mm": 6,
            "each_direction": True,
            "reference": "API 661 para 4.1.5",
        },
        "plug_hardness_cs": {
            "max_hrb": 68,
            "reference": "API 661 para 4.3.4",
        },
        "plug_hardness_ss": {
            "max_hrb": 82,
            "reference": "API 661 para 4.3.4",
        },
        "header_pressure_threshold": {
            "plug_type_above_psi": 435,
            "reference": "API 661 para 4.3.2",
        },
        "plenum_depth": {
            "min_mm": 915,
            "min_in": 36,
            "reference": "API 661 para 5.1.2",
        },
        "fan_coverage_ratio": {
            "min_percent": 40,
            "reference": "API 661 para 5.2.3",
        },
        "fin_strip_back": {
            "inlet_min_in": 1.0,
            "outlet_min_in": 0.5,
            "reference": "API 661 para 4.1.6",
        },
        "fin_density": {
            "typical_range": [7, 11],
            "unit": "fins/inch",
            "reference": "API 661 Table 3",
        },
        "fan_tip_clearance": {
            "4-5ft": 0.375,
            "6-8ft": 0.500,
            "9-12ft": 0.625,
            "13-18ft": 0.750,
            "19-28ft": 1.000,
            ">28ft": 1.250,
            "reference": "API 661 Table 6",
        },
        "tube_end_weld": {
            "type": "strength",
            "reference": "API 661 para 4.2.4",
        },
    }

    def __init__(self):
        """Initialize the API 661 validator."""
        self._load_standards_data()

    def _load_standards_data(self):
        """Load additional standards data from JSON if available."""
        data_path = Path(__file__).parent.parent.parent.parent / "data" / "standards" / "api_661_data.json"
        if data_path.exists():
            try:
                with open(data_path) as f:
                    self._external_data = json.load(f)
                logger.info(f"Loaded API 661 data from {data_path}")
            except Exception as e:
                logger.warning(f"Could not load API 661 data: {e}")
                self._external_data = {}
        else:
            self._external_data = {}

    def validate(self, extraction_result) -> API661ValidationResult:
        """
        Validate extracted drawing data against API 661 standards.

        Args:
            extraction_result: DrawingExtractionResult from PDF extractor

        Returns:
            API661ValidationResult with all check results
        """
        result = API661ValidationResult()

        # Run all API 661 checks
        checks = [
            self._check_tube_pitch(extraction_result),
            self._check_tube_support_spacing(extraction_result),
            self._check_bundle_lateral_movement(extraction_result),
            self._check_header_type_pressure(extraction_result),
            self._check_plug_hardness(extraction_result),
            self._check_fin_strip_back(extraction_result),
            self._check_fin_density(extraction_result),
            self._check_plenum_depth(extraction_result),
            self._check_fan_coverage(extraction_result),
            self._check_fan_tip_clearance(extraction_result),
            self._check_tube_end_weld(extraction_result),
            self._check_bundle_width(extraction_result),
        ]

        for check in checks:
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

                    # Create validation issue
                    result.issues.append(ValidationIssue(
                        severity=check.severity,
                        check_type="API_661",
                        message=check.message,
                        location=check.check_name,
                        suggestion=self._get_suggestion(check),
                        standard_reference=check.reference,
                    ))

        return result

    def _check_tube_pitch(self, data) -> Optional[API661CheckResult]:
        """Check tube pitch against API 661 standard (2.75" typical)."""
        # Look for tube pitch in dimensions or notes
        raw_text = getattr(data, 'raw_text', '')

        import re
        pitch_pattern = re.compile(r'(?:TUBE\s*)?PITCH[:\s]*(\d+\.?\d*)\s*(?:"|IN)?', re.I)
        match = pitch_pattern.search(raw_text)

        if match:
            actual_pitch = float(match.group(1))
            std = self.STANDARDS["tube_pitch"]
            expected = std["standard_in"]
            tolerance = std["tolerance_in"]

            passed = abs(actual_pitch - expected) <= tolerance

            return API661CheckResult(
                check_id="API661-001",
                check_name="Tube Pitch",
                passed=passed,
                actual_value=f"{actual_pitch}\"",
                expected_value=f"{expected}\" ± {tolerance}\"",
                reference=std["reference"],
                severity=ValidationSeverity.WARNING if not passed else ValidationSeverity.INFO,
                message=f"Tube pitch is {actual_pitch}\", expected {expected}\" ± {tolerance}\"" if not passed else "Tube pitch compliant",
            )

        return None

    def _check_tube_support_spacing(self, data) -> Optional[API661CheckResult]:
        """Check tube support spacing (max 6 ft / 1.83m per API 661)."""
        raw_text = getattr(data, 'raw_text', '')

        import re
        # Look for tube support spacing
        spacing_pattern = re.compile(
            r'(?:TUBE\s*)?SUPPORT\s*(?:SPACING|SPACE)[:\s]*(\d+\.?\d*)\s*(?:"|IN|FT|MM)?',
            re.I
        )
        match = spacing_pattern.search(raw_text)

        if match:
            actual_spacing = float(match.group(1))
            # Determine unit from context
            text_after = raw_text[match.end():match.end()+10].lower()
            if 'mm' in text_after:
                actual_mm = actual_spacing
            elif 'ft' in text_after:
                actual_mm = actual_spacing * 304.8
            else:
                # Assume inches
                actual_mm = actual_spacing * 25.4

            std = self.STANDARDS["tube_support_spacing"]
            max_mm = std["max_mm"]

            passed = actual_mm <= max_mm

            return API661CheckResult(
                check_id="API661-002",
                check_name="Tube Support Spacing",
                passed=passed,
                actual_value=f"{actual_mm:.0f}mm",
                expected_value=f"≤ {max_mm}mm (6 ft)",
                reference=std["reference"],
                severity=ValidationSeverity.ERROR if not passed else ValidationSeverity.INFO,
                message=f"Tube support spacing {actual_mm:.0f}mm exceeds max {max_mm}mm" if not passed else "Tube support spacing compliant",
            )

        return None

    def _check_bundle_lateral_movement(self, data) -> Optional[API661CheckResult]:
        """Check bundle lateral movement allowance (min 6mm each direction)."""
        raw_text = getattr(data, 'raw_text', '')

        import re
        # Look for bundle movement or expansion allowance
        movement_pattern = re.compile(
            r'(?:LATERAL|BUNDLE)\s*(?:MOVEMENT|EXPANSION|ALLOW(?:ANCE)?)[:\s]*(\d+\.?\d*)\s*(?:MM)?',
            re.I
        )
        match = movement_pattern.search(raw_text)

        if match:
            actual_mm = float(match.group(1))
            std = self.STANDARDS["bundle_lateral_movement"]
            min_mm = std["min_mm"]

            passed = actual_mm >= min_mm

            return API661CheckResult(
                check_id="API661-003",
                check_name="Bundle Lateral Movement",
                passed=passed,
                actual_value=f"{actual_mm}mm",
                expected_value=f"≥ {min_mm}mm each direction",
                reference=std["reference"],
                severity=ValidationSeverity.ERROR if not passed else ValidationSeverity.INFO,
                message=f"Bundle lateral movement {actual_mm}mm is less than required {min_mm}mm" if not passed else "Bundle lateral movement compliant",
            )

        return None

    def _check_header_type_pressure(self, data) -> Optional[API661CheckResult]:
        """Check header type is appropriate for pressure rating."""
        design_data = getattr(data, 'design_data', None)
        if not design_data:
            return None

        mawp = getattr(design_data, 'mawp_psi', 0) or getattr(design_data, 'design_pressure_psi', 0)
        if not mawp:
            return None

        std = self.STANDARDS["header_pressure_threshold"]
        threshold = std["plug_type_above_psi"]

        # Look for header type in text
        raw_text = getattr(data, 'raw_text', '')
        import re

        is_plug_type = bool(re.search(r'PLUG\s*(?:TYPE|HEADER)', raw_text, re.I))
        is_cover_plate = bool(re.search(r'COVER\s*PLATE', raw_text, re.I))

        if mawp > threshold:
            # Should be plug type above 435 psi
            passed = is_plug_type and not is_cover_plate

            return API661CheckResult(
                check_id="API661-004",
                check_name="Header Type vs Pressure",
                passed=passed,
                actual_value=f"MAWP: {mawp} psi, Header: {'Plug' if is_plug_type else 'Cover Plate' if is_cover_plate else 'Unknown'}",
                expected_value=f"Plug type required above {threshold} psi",
                reference=std["reference"],
                severity=ValidationSeverity.CRITICAL if not passed else ValidationSeverity.INFO,
                message=f"Header must be plug type for pressures above {threshold} psi" if not passed else "Header type appropriate for pressure",
            )

        return None

    def _check_plug_hardness(self, data) -> Optional[API661CheckResult]:
        """Check plug hardness specifications."""
        raw_text = getattr(data, 'raw_text', '')

        import re
        # Look for hardness specifications
        hardness_pattern = re.compile(
            r'(?:PLUG\s*)?HARDNESS[:\s]*(?:MAX\s*)?(?:HRB|HRC|ROCKWELL)\s*(\d+)',
            re.I
        )
        match = hardness_pattern.search(raw_text)

        if match:
            actual_hardness = int(match.group(1))

            # Determine if carbon steel or stainless
            is_stainless = bool(re.search(r'(?:316|304|SS|STAINLESS)', raw_text, re.I))

            if is_stainless:
                std = self.STANDARDS["plug_hardness_ss"]
                max_hrb = std["max_hrb"]
                material_type = "Stainless Steel"
            else:
                std = self.STANDARDS["plug_hardness_cs"]
                max_hrb = std["max_hrb"]
                material_type = "Carbon Steel"

            passed = actual_hardness <= max_hrb

            return API661CheckResult(
                check_id="API661-005",
                check_name="Plug Hardness",
                passed=passed,
                actual_value=f"HRB {actual_hardness} ({material_type})",
                expected_value=f"≤ HRB {max_hrb}",
                reference=std["reference"],
                severity=ValidationSeverity.ERROR if not passed else ValidationSeverity.INFO,
                message=f"Plug hardness HRB {actual_hardness} exceeds max HRB {max_hrb} for {material_type}" if not passed else "Plug hardness compliant",
            )

        return None

    def _check_fin_strip_back(self, data) -> Optional[API661CheckResult]:
        """Check fin strip back dimensions at tube ends."""
        raw_text = getattr(data, 'raw_text', '')

        import re
        # Look for fin strip back dimension
        strip_pattern = re.compile(
            r'(?:FIN\s*)?STRIP\s*BACK[:\s]*(\d+\.?\d*)\s*(?:"|IN)?',
            re.I
        )
        match = strip_pattern.search(raw_text)

        if match:
            actual_in = float(match.group(1))
            std = self.STANDARDS["fin_strip_back"]

            # Use inlet minimum as default check
            min_in = std["inlet_min_in"]

            passed = actual_in >= min_in

            return API661CheckResult(
                check_id="API661-006",
                check_name="Fin Strip Back",
                passed=passed,
                actual_value=f"{actual_in}\"",
                expected_value=f"≥ {min_in}\" (inlet)",
                reference=std["reference"],
                severity=ValidationSeverity.WARNING if not passed else ValidationSeverity.INFO,
                message=f"Fin strip back {actual_in}\" is less than minimum {min_in}\"" if not passed else "Fin strip back compliant",
            )

        return None

    def _check_fin_density(self, data) -> Optional[API661CheckResult]:
        """Check fin density is within typical range."""
        raw_text = getattr(data, 'raw_text', '')

        import re
        # Look for fin density (fins per inch)
        density_pattern = re.compile(
            r'(\d+)\s*(?:FINS?\s*/\s*(?:INCH|IN)|FPI)',
            re.I
        )
        match = density_pattern.search(raw_text)

        if match:
            actual_fpi = int(match.group(1))
            std = self.STANDARDS["fin_density"]
            typical_range = std["typical_range"]

            passed = typical_range[0] <= actual_fpi <= typical_range[1]

            return API661CheckResult(
                check_id="API661-007",
                check_name="Fin Density",
                passed=passed,
                actual_value=f"{actual_fpi} fins/inch",
                expected_value=f"{typical_range[0]}-{typical_range[1]} fins/inch (typical)",
                reference=std["reference"],
                severity=ValidationSeverity.INFO if not passed else ValidationSeverity.INFO,
                message=f"Fin density {actual_fpi} FPI outside typical range" if not passed else "Fin density within typical range",
            )

        return None

    def _check_plenum_depth(self, data) -> Optional[API661CheckResult]:
        """Check plenum depth meets minimum (36\" / 915mm)."""
        raw_text = getattr(data, 'raw_text', '')

        import re
        # Look for plenum depth
        depth_pattern = re.compile(
            r'PLENUM\s*(?:DEPTH|HEIGHT)[:\s]*(\d+\.?\d*)\s*(?:"|IN|MM)?',
            re.I
        )
        match = depth_pattern.search(raw_text)

        if match:
            actual = float(match.group(1))
            text_after = raw_text[match.end():match.end()+10].lower()

            std = self.STANDARDS["plenum_depth"]

            if 'mm' in text_after:
                actual_mm = actual
                min_val = std["min_mm"]
                unit = "mm"
            else:
                actual_mm = actual * 25.4
                min_val = std["min_mm"]
                unit = "in"

            passed = actual_mm >= std["min_mm"]

            return API661CheckResult(
                check_id="API661-008",
                check_name="Plenum Depth",
                passed=passed,
                actual_value=f"{actual}{unit}",
                expected_value=f"≥ {std['min_in']}\" ({std['min_mm']}mm)",
                reference=std["reference"],
                severity=ValidationSeverity.WARNING if not passed else ValidationSeverity.INFO,
                message=f"Plenum depth {actual}{unit} is less than minimum" if not passed else "Plenum depth compliant",
            )

        return None

    def _check_fan_coverage(self, data) -> Optional[API661CheckResult]:
        """Check fan coverage ratio (min 40%)."""
        raw_text = getattr(data, 'raw_text', '')

        import re
        # Look for fan coverage ratio
        coverage_pattern = re.compile(
            r'(?:FAN\s*)?COVERAGE\s*(?:RATIO)?[:\s]*(\d+\.?\d*)\s*%?',
            re.I
        )
        match = coverage_pattern.search(raw_text)

        if match:
            actual_pct = float(match.group(1))
            std = self.STANDARDS["fan_coverage_ratio"]
            min_pct = std["min_percent"]

            passed = actual_pct >= min_pct

            return API661CheckResult(
                check_id="API661-009",
                check_name="Fan Coverage Ratio",
                passed=passed,
                actual_value=f"{actual_pct}%",
                expected_value=f"≥ {min_pct}%",
                reference=std["reference"],
                severity=ValidationSeverity.WARNING if not passed else ValidationSeverity.INFO,
                message=f"Fan coverage ratio {actual_pct}% is below minimum {min_pct}%" if not passed else "Fan coverage ratio compliant",
            )

        return None

    def _check_fan_tip_clearance(self, data) -> Optional[API661CheckResult]:
        """Check fan tip clearance against API 661 Table 6."""
        raw_text = getattr(data, 'raw_text', '')

        import re
        # Look for fan diameter and tip clearance
        diameter_pattern = re.compile(r'FAN\s*(?:DIA(?:METER)?)?[:\s]*(\d+\.?\d*)\s*(?:FT|\'|FEET)?', re.I)
        clearance_pattern = re.compile(r'TIP\s*CLEARANCE[:\s]*(\d+\.?\d*)\s*(?:"|IN)?', re.I)

        dia_match = diameter_pattern.search(raw_text)
        clr_match = clearance_pattern.search(raw_text)

        if dia_match and clr_match:
            fan_dia_ft = float(dia_match.group(1))
            actual_clearance = float(clr_match.group(1))

            # Get max clearance from API 661 Table 6
            tip_clearance_table = self.STANDARDS["fan_tip_clearance"]
            max_clearance = 1.25  # Default for >28ft

            if fan_dia_ft <= 5:
                max_clearance = tip_clearance_table["4-5ft"]
            elif fan_dia_ft <= 8:
                max_clearance = tip_clearance_table["6-8ft"]
            elif fan_dia_ft <= 12:
                max_clearance = tip_clearance_table["9-12ft"]
            elif fan_dia_ft <= 18:
                max_clearance = tip_clearance_table["13-18ft"]
            elif fan_dia_ft <= 28:
                max_clearance = tip_clearance_table["19-28ft"]

            passed = actual_clearance <= max_clearance

            return API661CheckResult(
                check_id="API661-010",
                check_name="Fan Tip Clearance",
                passed=passed,
                actual_value=f"{actual_clearance}\" (fan dia: {fan_dia_ft}ft)",
                expected_value=f"≤ {max_clearance}\"",
                reference=tip_clearance_table["reference"],
                severity=ValidationSeverity.WARNING if not passed else ValidationSeverity.INFO,
                message=f"Fan tip clearance {actual_clearance}\" exceeds max {max_clearance}\" for {fan_dia_ft}ft fan" if not passed else "Fan tip clearance compliant",
            )

        return None

    def _check_tube_end_weld(self, data) -> Optional[API661CheckResult]:
        """Check tube-to-tubesheet weld is strength weld per API 661."""
        raw_text = getattr(data, 'raw_text', '')

        import re
        # Look for tube weld specification
        strength_weld = bool(re.search(r'STRENGTH\s*WELD', raw_text, re.I))
        seal_weld = bool(re.search(r'SEAL\s*WELD', raw_text, re.I))

        if strength_weld or seal_weld:
            std = self.STANDARDS["tube_end_weld"]
            passed = strength_weld

            return API661CheckResult(
                check_id="API661-011",
                check_name="Tube End Weld Type",
                passed=passed,
                actual_value="Strength weld" if strength_weld else "Seal weld",
                expected_value="Strength weld",
                reference=std["reference"],
                severity=ValidationSeverity.ERROR if not passed else ValidationSeverity.INFO,
                message="Tube-to-tubesheet weld should be strength weld, not seal weld" if not passed else "Tube end weld compliant",
            )

        return None

    def _check_bundle_width(self, data) -> Optional[API661CheckResult]:
        """Check bundle width vs frame width relationship."""
        # This would require specific dimension extraction
        # Placeholder for future enhancement
        return None

    def _get_suggestion(self, check: API661CheckResult) -> str:
        """Get fix suggestion for failed check."""
        suggestions = {
            "API661-001": "Verify tube pitch matches project specification or update drawing",
            "API661-002": "Add additional tube supports or reduce spacing to meet API 661 max",
            "API661-003": "Increase bundle lateral movement allowance to minimum 6mm each direction",
            "API661-004": "Change header type to plug type for pressures above 435 psi",
            "API661-005": "Specify softer plug material or verify hardness test requirements",
            "API661-006": "Increase fin strip back dimension at tube ends",
            "API661-007": "Verify fin density is appropriate for service conditions",
            "API661-008": "Increase plenum depth to meet API 661 minimum",
            "API661-009": "Increase fan diameter or reduce bundle width for better coverage",
            "API661-010": "Reduce fan tip clearance to meet API 661 Table 6 limits",
            "API661-011": "Specify strength weld for tube-to-tubesheet joint",
        }
        return suggestions.get(check.check_id, "Review and correct per API 661 requirements")

    def to_dict(self, result: API661ValidationResult) -> Dict[str, Any]:
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
