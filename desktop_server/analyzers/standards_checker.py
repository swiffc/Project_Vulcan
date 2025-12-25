"""
Standards Compliance Checker
============================
Check compliance with API 661, ASME VIII, TEMA, AWS D1.1, OSHA 1910.

Phase 24.24 Implementation
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("vulcan.analyzer.standards")


class ComplianceLevel(Enum):
    """Compliance check result level."""
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"
    NOT_APPLICABLE = "n/a"


@dataclass
class ComplianceCheck:
    """Result of a single compliance check."""
    standard: str  # API 661, ASME VIII, etc.
    section: str  # Specific section reference
    description: str
    level: ComplianceLevel = ComplianceLevel.PASS
    actual_value: str = ""
    required_value: str = ""
    notes: str = ""


@dataclass
class ComplianceReport:
    """Complete compliance report."""
    checks: List[ComplianceCheck] = field(default_factory=list)
    total_checks: int = 0
    passed: int = 0
    warnings: int = 0
    failed: int = 0
    not_applicable: int = 0
    summary: str = ""


class StandardsChecker:
    """
    Check design compliance with industry standards.
    Supports API 661, ASME VIII Div 1, TEMA, AWS D1.1, OSHA 1910.
    """

    # API 661 requirements
    API_661_TUBE_SUPPORT_SPACING_M = 1.83  # 6 feet max
    API_661_LATERAL_MOVEMENT_MM = 6.0  # Min each direction
    API_661_MAX_PLUG_HARDNESS_HB = 200  # Brinell hardness

    # TEMA requirements
    TEMA_MIN_TUBESHEET_FACTOR = 0.75  # Of ASME calc
    TEMA_MIN_LIGAMENT_FACTOR = 0.25  # Of pitch

    # OSHA 1910 requirements
    OSHA_HANDRAIL_HEIGHT_IN = 42.0
    OSHA_MIDRAIL_HEIGHT_IN = 21.0
    OSHA_TOEBOARD_HEIGHT_IN = 4.0
    OSHA_LADDER_CAGE_HEIGHT_FT = 20.0

    def __init__(self):
        pass

    def check_api_661(self, model_data: Dict[str, Any]) -> List[ComplianceCheck]:
        """Check API 661 compliance for ACHE."""
        checks = []

        # Check tube support spacing
        tube_support_spacing = model_data.get("tube_support_spacing_m")
        if tube_support_spacing is not None:
            check = ComplianceCheck(
                standard="API 661",
                section="7.1.6.1",
                description="Tube support spacing shall not exceed 1.83m (6 ft)",
                actual_value=f"{tube_support_spacing:.3f} m",
                required_value=f"≤ {self.API_661_TUBE_SUPPORT_SPACING_M} m",
            )
            if tube_support_spacing <= self.API_661_TUBE_SUPPORT_SPACING_M:
                check.level = ComplianceLevel.PASS
            else:
                check.level = ComplianceLevel.FAIL
                check.notes = f"Exceeds by {tube_support_spacing - self.API_661_TUBE_SUPPORT_SPACING_M:.3f} m"
            checks.append(check)

        # Check bundle lateral movement
        lateral_movement = model_data.get("bundle_lateral_movement_mm")
        if lateral_movement is not None:
            check = ComplianceCheck(
                standard="API 661",
                section="7.1.5.2",
                description="Tube bundle shall have minimum 6mm lateral movement each direction",
                actual_value=f"{lateral_movement:.1f} mm",
                required_value=f"≥ {self.API_661_LATERAL_MOVEMENT_MM} mm",
            )
            if lateral_movement >= self.API_661_LATERAL_MOVEMENT_MM:
                check.level = ComplianceLevel.PASS
            else:
                check.level = ComplianceLevel.FAIL
            checks.append(check)

        # Check header type for pressure
        design_pressure = model_data.get("design_pressure_psi", 0)
        header_type = model_data.get("header_type", "").lower()
        if header_type and design_pressure > 0:
            check = ComplianceCheck(
                standard="API 661",
                section="7.1.4.1",
                description="Header type appropriate for design pressure",
                actual_value=f"{header_type} at {design_pressure} psi",
            )
            # Plug headers typically limited to ~300 psi
            if "plug" in header_type and design_pressure > 300:
                check.level = ComplianceLevel.WARNING
                check.required_value = "Consider cover plate header above 300 psi"
            else:
                check.level = ComplianceLevel.PASS
                check.required_value = "Appropriate"
            checks.append(check)

        # Check plug hardness
        plug_hardness = model_data.get("plug_hardness_hb")
        if plug_hardness is not None:
            check = ComplianceCheck(
                standard="API 661",
                section="7.1.4.6",
                description="Plug hardness shall not exceed 200 HB",
                actual_value=f"{plug_hardness} HB",
                required_value=f"≤ {self.API_661_MAX_PLUG_HARDNESS_HB} HB",
            )
            if plug_hardness <= self.API_661_MAX_PLUG_HARDNESS_HB:
                check.level = ComplianceLevel.PASS
            else:
                check.level = ComplianceLevel.FAIL
            checks.append(check)

        return checks

    def check_asme_viii(self, model_data: Dict[str, Any]) -> List[ComplianceCheck]:
        """Check ASME VIII Div 1 compliance."""
        checks = []

        # Check pressure rating
        mawp = model_data.get("mawp_psi")
        design_pressure = model_data.get("design_pressure_psi")
        if mawp is not None and design_pressure is not None:
            check = ComplianceCheck(
                standard="ASME VIII",
                section="UG-21",
                description="MAWP shall exceed design pressure",
                actual_value=f"MAWP={mawp:.0f} psi, Design={design_pressure:.0f} psi",
                required_value="MAWP ≥ Design Pressure",
            )
            if mawp >= design_pressure:
                check.level = ComplianceLevel.PASS
                margin = (mawp - design_pressure) / design_pressure * 100
                check.notes = f"Margin: {margin:.1f}%"
            else:
                check.level = ComplianceLevel.FAIL
            checks.append(check)

        # Check joint efficiency
        joint_efficiency = model_data.get("joint_efficiency")
        if joint_efficiency is not None:
            check = ComplianceCheck(
                standard="ASME VIII",
                section="UW-12",
                description="Joint efficiency appropriate for examination level",
                actual_value=f"{joint_efficiency * 100:.0f}%",
            )
            if joint_efficiency == 1.0:
                check.required_value = "100% requires full RT/UT"
                check.level = ComplianceLevel.PASS
            elif joint_efficiency >= 0.85:
                check.required_value = "85% requires spot RT"
                check.level = ComplianceLevel.PASS
            elif joint_efficiency >= 0.70:
                check.required_value = "70% no RT required"
                check.level = ComplianceLevel.PASS
            else:
                check.level = ComplianceLevel.WARNING
                check.notes = "Verify joint efficiency is appropriate"
            checks.append(check)

        return checks

    def check_tema(self, model_data: Dict[str, Any]) -> List[ComplianceCheck]:
        """Check TEMA compliance."""
        checks = []

        # Check TEMA class
        tema_class = model_data.get("tema_class", "").upper()
        if tema_class:
            check = ComplianceCheck(
                standard="TEMA",
                section="General",
                description="TEMA class specified",
                actual_value=tema_class,
            )
            if tema_class in ["R", "C", "B"]:
                check.level = ComplianceLevel.PASS
                check.required_value = f"Class {tema_class} requirements apply"
            else:
                check.level = ComplianceLevel.WARNING
                check.notes = "Specify TEMA R, C, or B"
            checks.append(check)

        # Check ligament
        ligament_factor = model_data.get("ligament_factor")
        if ligament_factor is not None:
            check = ComplianceCheck(
                standard="TEMA",
                section="RCB-7.131",
                description="Minimum ligament between tube holes",
                actual_value=f"{ligament_factor * 100:.1f}% of pitch",
                required_value=f"≥ {self.TEMA_MIN_LIGAMENT_FACTOR * 100:.0f}% of pitch",
            )
            if ligament_factor >= self.TEMA_MIN_LIGAMENT_FACTOR:
                check.level = ComplianceLevel.PASS
            else:
                check.level = ComplianceLevel.FAIL
            checks.append(check)

        return checks

    def check_osha_1910(self, model_data: Dict[str, Any]) -> List[ComplianceCheck]:
        """Check OSHA 1910 compliance for platforms and ladders."""
        checks = []

        # Check handrail height
        handrail_height = model_data.get("handrail_height_in")
        if handrail_height is not None:
            check = ComplianceCheck(
                standard="OSHA 1910",
                section="1910.29(b)(1)",
                description="Handrail height 42 inches nominal",
                actual_value=f"{handrail_height:.1f} in",
                required_value=f"42 ± 3 in",
            )
            if 39 <= handrail_height <= 45:
                check.level = ComplianceLevel.PASS
            else:
                check.level = ComplianceLevel.FAIL
            checks.append(check)

        # Check toeboard height
        toeboard_height = model_data.get("toeboard_height_in")
        if toeboard_height is not None:
            check = ComplianceCheck(
                standard="OSHA 1910",
                section="1910.29(k)(1)",
                description="Toeboard minimum 4 inches high",
                actual_value=f"{toeboard_height:.1f} in",
                required_value=f"≥ {self.OSHA_TOEBOARD_HEIGHT_IN} in",
            )
            if toeboard_height >= self.OSHA_TOEBOARD_HEIGHT_IN:
                check.level = ComplianceLevel.PASS
            else:
                check.level = ComplianceLevel.FAIL
            checks.append(check)

        return checks

    def check_aws_d1_1(self, model_data: Dict[str, Any]) -> List[ComplianceCheck]:
        """Check AWS D1.1 weld compliance."""
        checks = []

        # Check weld NDE
        weld_nde = model_data.get("weld_nde_requirements", [])
        if weld_nde:
            check = ComplianceCheck(
                standard="AWS D1.1",
                section="6.0",
                description="Weld NDE requirements specified",
                actual_value=", ".join(weld_nde),
                required_value="Per WPS and design requirements",
            )
            check.level = ComplianceLevel.PASS
            checks.append(check)

        return checks

    def run_all_checks(self, model_data: Dict[str, Any]) -> ComplianceReport:
        """Run all compliance checks."""
        report = ComplianceReport()

        # Run each standard's checks
        report.checks.extend(self.check_api_661(model_data))
        report.checks.extend(self.check_asme_viii(model_data))
        report.checks.extend(self.check_tema(model_data))
        report.checks.extend(self.check_osha_1910(model_data))
        report.checks.extend(self.check_aws_d1_1(model_data))

        # Tally results
        for check in report.checks:
            report.total_checks += 1
            if check.level == ComplianceLevel.PASS:
                report.passed += 1
            elif check.level == ComplianceLevel.WARNING:
                report.warnings += 1
            elif check.level == ComplianceLevel.FAIL:
                report.failed += 1
            else:
                report.not_applicable += 1

        # Generate summary
        if report.failed > 0:
            report.summary = f"FAILED: {report.failed} non-compliant items require attention"
        elif report.warnings > 0:
            report.summary = f"PASSED with {report.warnings} warning(s)"
        else:
            report.summary = f"PASSED: All {report.passed} checks compliant"

        return report

    def to_dict(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run checks and return results as dictionary."""
        report = self.run_all_checks(model_data)

        return {
            "summary": report.summary,
            "total_checks": report.total_checks,
            "passed": report.passed,
            "warnings": report.warnings,
            "failed": report.failed,
            "checks": [
                {
                    "standard": c.standard,
                    "section": c.section,
                    "description": c.description,
                    "level": c.level.value,
                    "actual_value": c.actual_value,
                    "required_value": c.required_value,
                    "notes": c.notes,
                }
                for c in report.checks
            ],
        }
