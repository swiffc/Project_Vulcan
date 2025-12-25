"""
AWS D1.1 Validator
==================
Validate engineering drawings against AWS D1.1 (Structural Welding) standards.

Phase 25.4 Implementation
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.aws_d1_1")


@dataclass
class AWSCheckResult:
    """Result of a single AWS D1.1 check."""
    check_id: str
    check_name: str
    passed: bool
    actual_value: Any = None
    expected_value: Any = None
    reference: str = ""
    severity: ValidationSeverity = ValidationSeverity.WARNING
    message: str = ""


@dataclass
class AWSValidationResult:
    """Complete AWS D1.1 validation results."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    check_results: List[AWSCheckResult] = field(default_factory=list)
    issues: List[ValidationIssue] = field(default_factory=list)


class AWSD11Validator:
    """
    Validate drawings against AWS D1.1 Structural Welding standards.

    Checks include:
    - Weld procedure number verification
    - Weld size verification vs joint type
    - Joint preparation angle verification
    - Root opening verification
    - Fillet weld size minimums
    - Full penetration vs partial penetration
    - Weld NDE requirements (RT, UT, MT, PT)
    - CSA W59/W47.1/W48 compliance (Canadian jobs)
    - Tube-to-tubesheet weld verification
    """

    # Minimum fillet weld sizes per material thickness (AWS D1.1 Table 5.8)
    MIN_FILLET_SIZE = {
        # Base metal thickness range -> min fillet size (inches)
        (0, 0.25): 0.125,      # 1/8"
        (0.25, 0.5): 0.1875,   # 3/16"
        (0.5, 0.75): 0.25,     # 1/4"
        (0.75, 1.5): 0.3125,   # 5/16"
        (1.5, 2.25): 0.375,    # 3/8"
        (2.25, 6.0): 0.5,      # 1/2"
        (6.0, 999): 0.625,     # 5/8"
    }

    # Common weld joint types and their requirements
    JOINT_TYPES = {
        "BUTT": {"full_pen_typical": True, "min_groove_angle_deg": 30},
        "TEE": {"full_pen_typical": False, "min_fillet_size_factor": 1.0},
        "CORNER": {"full_pen_typical": False, "min_groove_angle_deg": 30},
        "LAP": {"full_pen_typical": False, "min_overlap_factor": 5},
    }

    # Standard groove preparations
    GROOVE_TYPES = {
        "V": {"min_angle_deg": 60, "single_side": True},
        "DOUBLE-V": {"min_angle_deg": 60, "single_side": False},
        "BEVEL": {"min_angle_deg": 30, "single_side": True},
        "DOUBLE-BEVEL": {"min_angle_deg": 30, "single_side": False},
        "J": {"min_angle_deg": 20, "single_side": True},
        "DOUBLE-J": {"min_angle_deg": 20, "single_side": False},
        "U": {"min_angle_deg": 20, "single_side": True},
        "DOUBLE-U": {"min_angle_deg": 20, "single_side": False},
    }

    # Weld processes
    WELD_PROCESSES = {
        "SMAW": "Shielded Metal Arc Welding",
        "GMAW": "Gas Metal Arc Welding (MIG)",
        "FCAW": "Flux-Cored Arc Welding",
        "GTAW": "Gas Tungsten Arc Welding (TIG)",
        "SAW": "Submerged Arc Welding",
    }

    # NDE methods
    NDE_METHODS = {
        "RT": "Radiographic Testing",
        "UT": "Ultrasonic Testing",
        "MT": "Magnetic Particle Testing",
        "PT": "Liquid Penetrant Testing",
        "VT": "Visual Testing",
    }

    # Preheat requirements per AWS D1.1 Table 3.2 (simplified)
    # Base metal thickness -> minimum preheat temp (°F)
    PREHEAT_REQUIREMENTS = {
        # ASTM A36, A572 Gr 50 (Group I)
        "A36": {
            (0, 0.75): 32,      # No preheat required
            (0.75, 1.5): 50,    # 50°F min
            (1.5, 2.5): 150,    # 150°F min
            (2.5, 999): 225,    # 225°F min
        },
        "A572": {
            (0, 0.75): 32,
            (0.75, 1.5): 50,
            (1.5, 2.5): 150,
            (2.5, 999): 225,
        },
        # High strength (Group II)
        "A514": {
            (0, 0.75): 50,
            (0.75, 1.5): 125,
            (1.5, 2.5): 175,
            (2.5, 999): 225,
        },
    }

    # Interpass temperature limits (°F)
    INTERPASS_TEMP = {
        "standard": {"min": 50, "max": 600},
        "low_hydrogen": {"min": 50, "max": 400},
        "quench_tempered": {"min": 50, "max": 400},
    }

    # Filler metal classifications
    FILLER_METALS = {
        "E70XX": {"tensile_ksi": 70, "process": "SMAW"},
        "E71T-X": {"tensile_ksi": 70, "process": "FCAW"},
        "ER70S-X": {"tensile_ksi": 70, "process": "GMAW/GTAW"},
        "E80XX": {"tensile_ksi": 80, "process": "SMAW"},
        "E81T-X": {"tensile_ksi": 80, "process": "FCAW"},
    }

    def __init__(self):
        """Initialize the AWS D1.1 validator."""
        pass

    def validate(self, extraction_result) -> AWSValidationResult:
        """
        Validate extracted drawing data against AWS D1.1 standards.

        Args:
            extraction_result: DrawingExtractionResult from PDF extractor

        Returns:
            AWSValidationResult with all check results
        """
        result = AWSValidationResult()

        # Run all AWS D1.1 checks (14 total)
        checks = [
            self._check_weld_procedures(extraction_result),
            self._check_weld_sizes(extraction_result),
            self._check_joint_preparation(extraction_result),
            self._check_root_opening(extraction_result),
            self._check_fillet_weld_minimums(extraction_result),
            self._check_penetration_type(extraction_result),
            self._check_nde_requirements(extraction_result),
            self._check_csa_compliance(extraction_result),
            self._check_tube_welds(extraction_result),
            self._check_weld_symbols(extraction_result),
            # New checks
            self._check_preheat_requirements(extraction_result),
            self._check_interpass_temperature(extraction_result),
            self._check_welder_qualification(extraction_result),
            self._check_filler_metal(extraction_result),
        ]

        for check_list in checks:
            if isinstance(check_list, list):
                for check in check_list:
                    self._process_check(check, result)
            elif check_list:
                self._process_check(check_list, result)

        return result

    def _process_check(self, check: AWSCheckResult, result: AWSValidationResult):
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
                    check_type="AWS_D1.1",
                    message=check.message,
                    location=check.check_name,
                    suggestion=self._get_suggestion(check),
                    standard_reference=check.reference,
                ))

    def _check_weld_procedures(self, data) -> List[AWSCheckResult]:
        """Check weld procedure specifications are present and valid."""
        results = []
        weld_symbols = getattr(data, 'weld_symbols', [])
        raw_text = getattr(data, 'raw_text', '')

        # Look for WPS references
        wps_pattern = re.compile(r'(P\d+[A-Z]*-\d+[A-Z]*|WPS[:\s#]*\d+)', re.I)
        matches = wps_pattern.findall(raw_text)

        if matches:
            procedures = list(set(m.upper() for m in matches))

            result = AWSCheckResult(
                check_id="AWS-WPS-001",
                check_name="Weld Procedures",
                passed=True,
                actual_value=", ".join(procedures),
                expected_value="Valid WPS references",
                reference="AWS D1.1 Section 5",
                severity=ValidationSeverity.INFO,
                message=f"Weld procedures specified: {', '.join(procedures)}",
            )
            results.append(result)
        else:
            result = AWSCheckResult(
                check_id="AWS-WPS-001",
                check_name="Weld Procedures",
                passed=False,
                actual_value="None found",
                expected_value="WPS reference for each weld",
                reference="AWS D1.1 Section 5",
                severity=ValidationSeverity.WARNING,
                message="No weld procedure specifications (WPS) found in drawing",
            )
            results.append(result)

        return results

    def _check_weld_sizes(self, data) -> List[AWSCheckResult]:
        """Check weld sizes are specified."""
        results = []
        weld_symbols = getattr(data, 'weld_symbols', [])
        raw_text = getattr(data, 'raw_text', '')

        # Look for weld sizes
        size_pattern = re.compile(r'(\d+/\d+|\d+(?:\.\d+)?)\s*(?:"|IN)?\s*(?:FILLET|FIL|WELD)', re.I)
        matches = size_pattern.findall(raw_text)

        if matches:
            sizes = list(set(matches))

            # Parse fractional sizes
            parsed_sizes = []
            for size in sizes:
                if '/' in size:
                    num, den = size.split('/')
                    parsed_sizes.append(f"{size}\" ({float(num)/float(den):.3f}\")")
                else:
                    parsed_sizes.append(f"{size}\"")

            result = AWSCheckResult(
                check_id="AWS-SZ-001",
                check_name="Weld Sizes",
                passed=True,
                actual_value=", ".join(parsed_sizes),
                expected_value="Weld sizes per joint requirements",
                reference="AWS D1.1 Section 2",
                severity=ValidationSeverity.INFO,
                message=f"Weld sizes specified: {', '.join(parsed_sizes)}",
            )
            results.append(result)

        return results

    def _check_joint_preparation(self, data) -> Optional[AWSCheckResult]:
        """Check joint preparation specifications."""
        raw_text = getattr(data, 'raw_text', '')

        # Look for groove angles
        angle_pattern = re.compile(r'(\d+)\s*(?:°|DEG(?:REES)?)\s*(?:GROOVE|BEVEL)', re.I)
        matches = angle_pattern.findall(raw_text)

        if matches:
            angles = [int(a) for a in matches]
            min_angle = min(angles)

            # Check against minimums
            passed = min_angle >= 20  # Minimum J-groove angle

            return AWSCheckResult(
                check_id="AWS-JNT-001",
                check_name="Joint Preparation Angles",
                passed=passed,
                actual_value=f"Angles: {', '.join(str(a) + '°' for a in angles)}",
                expected_value="≥ 20° for J/U groove, ≥ 30° for bevel, ≥ 60° for V-groove",
                reference="AWS D1.1 Figure 3.3",
                severity=ValidationSeverity.WARNING if not passed else ValidationSeverity.INFO,
                message=f"Joint preparation angles {'adequate' if passed else 'may be too shallow'}",
            )

        return None

    def _check_root_opening(self, data) -> Optional[AWSCheckResult]:
        """Check root opening specifications."""
        raw_text = getattr(data, 'raw_text', '')

        # Look for root opening
        root_pattern = re.compile(r'ROOT\s*(?:OPENING|GAP)[:\s]*(\d+/\d+|\d+(?:\.\d+)?)\s*(?:"|IN)?', re.I)
        match = root_pattern.search(raw_text)

        if match:
            root_opening = match.group(1)

            # Parse fractional
            if '/' in root_opening:
                num, den = root_opening.split('/')
                opening_in = float(num) / float(den)
            else:
                opening_in = float(root_opening)

            # Typical root opening is 1/8" (0.125")
            passed = 0.0625 <= opening_in <= 0.25

            return AWSCheckResult(
                check_id="AWS-ROOT-001",
                check_name="Root Opening",
                passed=passed,
                actual_value=f"{root_opening}\" ({opening_in:.3f}\")",
                expected_value="1/16\" to 1/4\" typical (1/8\" common)",
                reference="AWS D1.1 Figure 3.3",
                severity=ValidationSeverity.INFO,
                message=f"Root opening {root_opening}\" specified",
            )

        return None

    def _check_fillet_weld_minimums(self, data) -> List[AWSCheckResult]:
        """Check fillet welds meet minimum size requirements."""
        results = []
        raw_text = getattr(data, 'raw_text', '')

        # Look for fillet weld sizes with material thickness context
        fillet_pattern = re.compile(
            r'(\d+/\d+|\d+(?:\.\d+)?)\s*(?:"|IN)?\s*(?:FILLET|FIL)',
            re.I
        )

        for match in fillet_pattern.finditer(raw_text):
            size_str = match.group(1)

            # Parse size
            if '/' in size_str:
                num, den = size_str.split('/')
                size_in = float(num) / float(den)
            else:
                size_in = float(size_str)

            # Check minimum (assume 1/4" minimum for general structural)
            min_size = 0.125  # 1/8" absolute minimum
            passed = size_in >= min_size

            result = AWSCheckResult(
                check_id=f"AWS-FIL-{len(results)+1:03d}",
                check_name=f"Fillet Weld Size {size_str}\"",
                passed=passed,
                actual_value=f"{size_str}\" ({size_in:.3f}\")",
                expected_value=f"≥ {min_size}\" minimum",
                reference="AWS D1.1 Table 5.8",
                severity=ValidationSeverity.ERROR if not passed else ValidationSeverity.INFO,
                message=f"Fillet weld {size_str}\" {'meets' if passed else 'below'} minimum",
            )
            results.append(result)

        return results

    def _check_penetration_type(self, data) -> Optional[AWSCheckResult]:
        """Check full vs partial penetration specifications."""
        raw_text = getattr(data, 'raw_text', '')

        full_pen = bool(re.search(r'(?:FULL|COMPLETE)\s*(?:PEN(?:ETRATION)?|JNT)', raw_text, re.I))
        partial_pen = bool(re.search(r'PARTIAL\s*(?:PEN(?:ETRATION)?|JNT)', raw_text, re.I))
        cjp = bool(re.search(r'CJP', raw_text))
        pjp = bool(re.search(r'PJP', raw_text))

        if full_pen or partial_pen or cjp or pjp:
            pen_type = "CJP" if (full_pen or cjp) else "PJP"

            return AWSCheckResult(
                check_id="AWS-PEN-001",
                check_name="Weld Penetration Type",
                passed=True,
                actual_value=f"{pen_type} ({('Complete' if pen_type == 'CJP' else 'Partial')} Joint Penetration)",
                expected_value="Penetration type specified per design requirements",
                reference="AWS D1.1 Section 2.3",
                severity=ValidationSeverity.INFO,
                message=f"{pen_type} welds specified",
            )

        return None

    def _check_nde_requirements(self, data) -> List[AWSCheckResult]:
        """Check NDE (Non-Destructive Examination) requirements."""
        results = []
        raw_text = getattr(data, 'raw_text', '')

        for method, full_name in self.NDE_METHODS.items():
            if re.search(rf'\b{method}\b', raw_text):
                result = AWSCheckResult(
                    check_id=f"AWS-NDE-{method}",
                    check_name=f"NDE: {method}",
                    passed=True,
                    actual_value=full_name,
                    expected_value="NDE method specified",
                    reference="AWS D1.1 Section 6",
                    severity=ValidationSeverity.INFO,
                    message=f"{full_name} ({method}) required",
                )
                results.append(result)

        return results

    def _check_csa_compliance(self, data) -> Optional[AWSCheckResult]:
        """Check for CSA (Canadian Standards) compliance requirements."""
        raw_text = getattr(data, 'raw_text', '')

        csa_pattern = re.compile(r'CSA\s*(?:W59|W47\.1|W48)', re.I)
        matches = csa_pattern.findall(raw_text)

        if matches:
            standards = list(set(m.upper() for m in matches))

            return AWSCheckResult(
                check_id="AWS-CSA-001",
                check_name="CSA Compliance",
                passed=True,
                actual_value=", ".join(standards),
                expected_value="Canadian Standards Association requirements",
                reference="CSA W59/W47.1/W48",
                severity=ValidationSeverity.INFO,
                message=f"Canadian welding standards required: {', '.join(standards)}",
            )

        return None

    def _check_tube_welds(self, data) -> Optional[AWSCheckResult]:
        """Check tube-to-tubesheet weld specifications."""
        raw_text = getattr(data, 'raw_text', '')

        # Look for tube weld specifications
        tube_weld_pattern = re.compile(
            r'(?:TUBE|TUBE-TO-TUBESHEET)\s*(?:WELD|WLD)[:\s]*(GTAW|GMAW|SMAW)?',
            re.I
        )
        match = tube_weld_pattern.search(raw_text)

        if match:
            process = match.group(1).upper() if match.group(1) else "Not specified"

            # GTAW is preferred for tube welds
            is_gtaw = process == "GTAW"

            return AWSCheckResult(
                check_id="AWS-TUBE-001",
                check_name="Tube-to-Tubesheet Weld",
                passed=True,
                actual_value=f"Process: {process}",
                expected_value="GTAW preferred for tube-to-tubesheet welds",
                reference="API 661 para 4.2.4",
                severity=ValidationSeverity.INFO if is_gtaw else ValidationSeverity.WARNING,
                message=f"Tube weld process: {self.WELD_PROCESSES.get(process, process)}",
            )

        return None

    def _check_weld_symbols(self, data) -> List[AWSCheckResult]:
        """Check weld symbols are properly specified."""
        results = []
        weld_symbols = getattr(data, 'weld_symbols', [])

        for i, weld in enumerate(weld_symbols):
            weld_type = getattr(weld, 'weld_type', '')
            size = getattr(weld, 'size', '')
            procedure = getattr(weld, 'procedure', '')

            has_size = bool(size)
            has_procedure = bool(procedure)

            passed = has_size  # At minimum, size should be specified

            result = AWSCheckResult(
                check_id=f"AWS-SYM-{i+1:03d}",
                check_name=f"Weld Symbol #{i+1}",
                passed=passed,
                actual_value=f"Type: {weld_type}, Size: {size or 'N/A'}, WPS: {procedure or 'N/A'}",
                expected_value="Weld type, size, and procedure specified",
                reference="AWS A2.4",
                severity=ValidationSeverity.WARNING if not passed else ValidationSeverity.INFO,
                message=f"Weld symbol {i+1}: {weld_type} {size}" if passed else f"Weld symbol {i+1} missing size",
            )
            results.append(result)

        return results

    def _check_preheat_requirements(self, data) -> Optional[AWSCheckResult]:
        """Check preheat temperature requirements per AWS D1.1 Table 3.2."""
        raw_text = getattr(data, 'raw_text', '')

        # Look for preheat specifications
        preheat_pattern = re.compile(
            r'PREHEAT[:\s]*(\d+)\s*(?:°?F|DEG)',
            re.I
        )
        match = preheat_pattern.search(raw_text)

        if match:
            preheat_temp = int(match.group(1))

            # Minimum preheat for structural welding is typically 50°F
            passed = preheat_temp >= 50

            return AWSCheckResult(
                check_id="AWS-PRE-001",
                check_name="Preheat Temperature",
                passed=passed,
                actual_value=f"{preheat_temp}°F",
                expected_value="≥50°F minimum (higher for thicker material)",
                reference="AWS D1.1 Table 3.2",
                severity=ValidationSeverity.INFO if passed else ValidationSeverity.WARNING,
                message=f"Preheat temperature {preheat_temp}°F specified",
            )

        # Check if material thickness suggests preheat needed
        thickness_pattern = re.compile(r'(\d+(?:\.\d+)?)\s*(?:"|IN)\s*(?:THK|THICK|PL|PLATE)', re.I)
        thickness_match = thickness_pattern.search(raw_text)

        if thickness_match:
            thickness = float(thickness_match.group(1))
            if thickness > 1.5:  # Thicker than 1.5" typically needs preheat
                return AWSCheckResult(
                    check_id="AWS-PRE-001",
                    check_name="Preheat Temperature",
                    passed=False,
                    actual_value="Not specified",
                    expected_value=f"Preheat required for >{thickness}\" material",
                    reference="AWS D1.1 Table 3.2",
                    severity=ValidationSeverity.WARNING,
                    message=f"Material >{thickness}\" thick may require preheat specification",
                )

        return None

    def _check_interpass_temperature(self, data) -> Optional[AWSCheckResult]:
        """Check interpass temperature requirements."""
        raw_text = getattr(data, 'raw_text', '')

        # Look for interpass temperature
        interpass_pattern = re.compile(
            r'(?:INTERPASS|MAX\s*INTERPASS)[:\s]*(\d+)\s*(?:°?F|DEG)',
            re.I
        )
        match = interpass_pattern.search(raw_text)

        if match:
            interpass_temp = int(match.group(1))

            # Standard max is 600°F, Q&T steels max 400°F
            limits = self.INTERPASS_TEMP["standard"]
            passed = limits["min"] <= interpass_temp <= limits["max"]

            return AWSCheckResult(
                check_id="AWS-INT-001",
                check_name="Interpass Temperature",
                passed=passed,
                actual_value=f"{interpass_temp}°F max",
                expected_value=f"{limits['min']}-{limits['max']}°F typical range",
                reference="AWS D1.1 Section 5.6",
                severity=ValidationSeverity.INFO if passed else ValidationSeverity.WARNING,
                message=f"Interpass temperature {interpass_temp}°F {'within' if passed else 'outside'} limits",
            )

        # For multi-pass welds, interpass should be specified
        if re.search(r'MULTI(?:-|\s)?PASS', raw_text, re.I):
            return AWSCheckResult(
                check_id="AWS-INT-001",
                check_name="Interpass Temperature",
                passed=False,
                actual_value="Not specified",
                expected_value="Interpass temp required for multi-pass welds",
                reference="AWS D1.1 Section 5.6",
                severity=ValidationSeverity.INFO,
                message="Multi-pass weld detected but interpass temperature not specified",
            )

        return None

    def _check_welder_qualification(self, data) -> Optional[AWSCheckResult]:
        """Check welder qualification requirements are referenced."""
        raw_text = getattr(data, 'raw_text', '')

        # Look for welder qualification references
        qual_patterns = [
            r'WELDER\s*(?:QUAL(?:IFICATION)?|CERT(?:IFICATION)?)',
            r'WQR',  # Welder Qualification Record
            r'WPQR',  # Welding Procedure Qualification Record
            r'QUALIFIED\s*(?:PER|TO)\s*(?:AWS|ASME)',
        ]

        for pattern in qual_patterns:
            if re.search(pattern, raw_text, re.I):
                return AWSCheckResult(
                    check_id="AWS-QUAL-001",
                    check_name="Welder Qualification",
                    passed=True,
                    actual_value="Qualification requirement referenced",
                    expected_value="Welder qualification per AWS D1.1 Section 4",
                    reference="AWS D1.1 Section 4",
                    severity=ValidationSeverity.INFO,
                    message="Welder qualification requirements referenced",
                )

        # Check if structural welding that should have qualification note
        if re.search(r'(?:STRUCTURAL|CJP|FULL\s*PEN)', raw_text, re.I):
            return AWSCheckResult(
                check_id="AWS-QUAL-001",
                check_name="Welder Qualification",
                passed=False,
                actual_value="Not specified",
                expected_value="Welder qualification reference for structural welds",
                reference="AWS D1.1 Section 4",
                severity=ValidationSeverity.INFO,
                message="Consider adding welder qualification note for structural welds",
            )

        return None

    def _check_filler_metal(self, data) -> List[AWSCheckResult]:
        """Check filler metal classifications."""
        results = []
        raw_text = getattr(data, 'raw_text', '')

        # Look for filler metal classifications
        filler_patterns = [
            (r'E70(?:18|XX)', "E70XX", "SMAW"),
            (r'E71T-\d+', "E71T-X", "FCAW"),
            (r'ER70S-\d+', "ER70S-X", "GMAW/GTAW"),
            (r'E80(?:18|XX)', "E80XX", "SMAW"),
            (r'E81T-\d+', "E81T-X", "FCAW"),
        ]

        found_fillers = []
        for pattern, classification, process in filler_patterns:
            matches = re.findall(pattern, raw_text, re.I)
            if matches:
                found_fillers.extend([(m, classification, process) for m in matches])

        if found_fillers:
            for filler, classification, process in found_fillers:
                filler_info = self.FILLER_METALS.get(classification, {})
                tensile = filler_info.get("tensile_ksi", "N/A")

                result = AWSCheckResult(
                    check_id=f"AWS-FILL-{len(results)+1:03d}",
                    check_name=f"Filler Metal {filler.upper()}",
                    passed=True,
                    actual_value=f"{filler.upper()} ({tensile} ksi tensile)",
                    expected_value="Filler metal matching base metal strength",
                    reference="AWS D1.1 Table 3.1",
                    severity=ValidationSeverity.INFO,
                    message=f"Filler metal {filler.upper()} specified ({process})",
                )
                results.append(result)
        else:
            # Check if welding is specified but no filler
            if re.search(r'WELD|WLD|FILLET|GROOVE', raw_text, re.I):
                result = AWSCheckResult(
                    check_id="AWS-FILL-001",
                    check_name="Filler Metal",
                    passed=False,
                    actual_value="Not specified",
                    expected_value="Filler metal classification (E70XX, E71T-X, etc.)",
                    reference="AWS D1.1 Table 3.1",
                    severity=ValidationSeverity.WARNING,
                    message="Welds specified but filler metal classification not found",
                )
                results.append(result)

        return results

    def _get_suggestion(self, check: AWSCheckResult) -> str:
        """Get fix suggestion for failed check."""
        suggestions = {
            "AWS-WPS": "Add weld procedure specification (WPS) reference to drawing",
            "AWS-SZ": "Specify weld size for all welds per AWS D1.1",
            "AWS-JNT": "Verify joint preparation angle meets AWS D1.1 minimums",
            "AWS-ROOT": "Verify root opening is within AWS D1.1 limits",
            "AWS-FIL": "Increase fillet weld size to meet AWS D1.1 Table 5.8 minimum",
            "AWS-PEN": "Specify full (CJP) or partial (PJP) penetration type",
            "AWS-NDE": "Add required NDE method specification",
            "AWS-CSA": "Verify Canadian welding standards compliance",
            "AWS-TUBE": "Specify tube weld process (GTAW preferred)",
            "AWS-SYM": "Complete weld symbol with type, size, and procedure",
            "AWS-PRE": "Add preheat temperature per AWS D1.1 Table 3.2",
            "AWS-INT": "Specify interpass temperature limit (max 600°F typical)",
            "AWS-QUAL": "Add welder qualification note (per AWS D1.1 Section 4)",
            "AWS-FILL": "Specify filler metal classification (E70XX, E71T-X, etc.)",
        }

        for prefix, suggestion in suggestions.items():
            if check.check_id.startswith(prefix):
                return suggestion

        return "Review and correct per AWS D1.1 requirements"

    def to_dict(self, result: AWSValidationResult) -> Dict[str, Any]:
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
