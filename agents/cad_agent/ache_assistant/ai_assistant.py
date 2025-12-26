"""
ACHE AI Assistant Module
Phase 24.7 - AI-Powered Design Assistance for Air Cooled Heat Exchangers

Provides intelligent assistance for:
- Design recommendations
- API 661 compliance checking
- Optimization suggestions
- Knowledge base queries
- Natural language interaction
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import json

logger = logging.getLogger("vulcan.ache.ai_assistant")


class QueryType(Enum):
    """Types of AI queries."""
    DESIGN_RECOMMENDATION = "design_recommendation"
    COMPLIANCE_CHECK = "compliance_check"
    OPTIMIZATION = "optimization"
    KNOWLEDGE_QUERY = "knowledge_query"
    TROUBLESHOOTING = "troubleshooting"
    CALCULATION = "calculation"


class ComplianceStatus(Enum):
    """Compliance check status."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    WARNING = "warning"
    NEEDS_REVIEW = "needs_review"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class ComplianceIssue:
    """Single compliance issue or warning."""
    code_reference: str
    requirement: str
    actual_value: Any
    required_value: Any
    status: ComplianceStatus
    severity: str = "medium"  # low, medium, high, critical
    recommendation: str = ""


@dataclass
class ComplianceReport:
    """Complete compliance check report."""
    standard: str = "API 661"
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    issues: List[ComplianceIssue] = field(default_factory=list)
    is_compliant: bool = True
    summary: str = ""


@dataclass
class DesignRecommendation:
    """AI-generated design recommendation."""
    category: str
    recommendation: str
    rationale: str
    impact: str = "medium"  # low, medium, high
    references: List[str] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)


@dataclass
class OptimizationSuggestion:
    """Optimization suggestion with potential savings."""
    area: str
    current_state: str
    suggested_change: str
    potential_benefit: str
    estimated_savings: Dict[str, Any] = field(default_factory=dict)
    implementation_effort: str = "medium"


class ACHEKnowledgeBase:
    """
    Knowledge base for ACHE design.

    Contains API 661 requirements, best practices,
    and design guidelines.
    """

    API_661_REQUIREMENTS = {
        "tube_bundle": {
            "max_tube_length_m": 12.0,
            "min_tube_wall_mm": 2.11,  # BWG 14
            "max_tube_od_mm": 38.1,  # 1.5"
            "min_tube_od_mm": 19.05,  # 0.75"
            "tube_pitch_ratio": {"triangular": 1.25, "square": 1.25},
        },
        "header_box": {
            "min_thickness_mm": 9.5,  # Per pressure
            "min_corrosion_allowance_mm": 3.0,
            "nozzle_reinforcement_required": True,
        },
        "fan": {
            "max_tip_speed_m_s": 61.0,  # 200 ft/s
            "min_blade_clearance_mm": 12.7,  # 0.5"
            "vibration_limit_mm_s": 3.0,
        },
        "structural": {
            "wind_speed_m_s": 40.0,  # Design wind
            "seismic_factor": 0.0,  # Site specific
            "deflection_limit": "L/240",
        },
        "access": {
            "min_walkway_width_mm": 450,
            "handrail_height_mm": 1070,
            "ladder_cage_height_m": 6.1,
        },
    }

    DESIGN_GUIDELINES = {
        "tube_selection": [
            "Use finned tubes for air-cooled service",
            "Select tube material based on process fluid corrosivity",
            "Standard fin heights: 12.7mm (0.5\") for most applications",
            "Consider bi-metallic tubes for severe services",
        ],
        "thermal_design": [
            "Maintain minimum 10°C approach temperature",
            "Design for fouled conditions with appropriate margin",
            "Consider process-side maldistribution effects",
            "Air recirculation can reduce effective MTD by 3-10°C",
        ],
        "mechanical_design": [
            "Header boxes per ASME Section VIII Div. 1",
            "Tube-to-tubesheet joints: strength welded for severe service",
            "Plugs required for tube inspection access",
            "Expansion joints for long bundles or high temperature difference",
        ],
        "fan_selection": [
            "Induced draft preferred for hot services",
            "Forced draft for clean, non-fouling services",
            "Auto-variable pitch for significant ambient temperature variation",
            "Multiple fans per bay for redundancy",
        ],
    }

    TROUBLESHOOTING_GUIDES = {
        "high_process_outlet_temp": {
            "possible_causes": [
                "Insufficient air flow",
                "Fouled tubes (air or process side)",
                "Fan blade pitch incorrect",
                "High ambient temperature",
                "Process flow maldistribution",
            ],
            "diagnostic_steps": [
                "Check fan operation and blade angles",
                "Measure air flow rate",
                "Inspect tubes for fouling",
                "Verify process flow distribution",
                "Check for air recirculation",
            ],
            "solutions": [
                "Increase fan speed or blade pitch",
                "Clean tube bundle",
                "Install wind walls to prevent recirculation",
                "Optimize process distribution",
            ],
        },
        "excessive_vibration": {
            "possible_causes": [
                "Fan imbalance",
                "Loose blade or hub",
                "Resonance with structure",
                "Bearing wear",
            ],
            "diagnostic_steps": [
                "Measure vibration levels at bearings",
                "Check fan balance",
                "Verify natural frequency vs. operating speed",
                "Inspect bearings and couplings",
            ],
            "solutions": [
                "Rebalance fan",
                "Tighten all connections",
                "Add stiffening if resonance issue",
                "Replace worn bearings",
            ],
        },
        "tube_leaks": {
            "possible_causes": [
                "Corrosion",
                "Erosion at inlet",
                "Vibration fatigue",
                "Thermal cycling",
                "Manufacturing defect",
            ],
            "diagnostic_steps": [
                "Perform hydrostatic test",
                "Locate leak with soap solution or tracer gas",
                "Inspect failed tubes metallurgically",
                "Review operating history",
            ],
            "solutions": [
                "Plug leaking tubes (up to 10%)",
                "Retube if extensive damage",
                "Address root cause (corrosion, vibration)",
                "Consider material upgrade",
            ],
        },
    }


class ACHEAssistant:
    """
    AI-powered assistant for ACHE design and analysis.

    Implements Phase 24.7: AI Features

    Capabilities:
    - Design recommendations based on inputs
    - API 661 compliance checking
    - Performance optimization suggestions
    - Troubleshooting assistance
    - Knowledge base queries
    """

    def __init__(self, llm_provider: Optional[Callable] = None):
        """
        Initialize ACHE assistant.

        Args:
            llm_provider: Optional LLM function for advanced queries
        """
        self._kb = ACHEKnowledgeBase()
        self._llm = llm_provider
        self._context: Dict[str, Any] = {}

    def set_context(self, ache_data: Dict[str, Any]) -> None:
        """Set ACHE design context for queries."""
        self._context = ache_data
        logger.info("ACHE context updated")

    def check_api661_compliance(
        self,
        ache_properties: Dict[str, Any],
    ) -> ComplianceReport:
        """
        Check ACHE design against API 661 requirements.

        Args:
            ache_properties: Extracted ACHE properties

        Returns:
            ComplianceReport with all findings
        """
        report = ComplianceReport(standard="API 661 / ISO 13706")
        issues = []

        try:
            # Tube bundle checks
            tube_data = ache_properties.get("tube_bundle", {})
            if tube_data:
                issues.extend(self._check_tube_bundle(tube_data))

            # Header box checks
            header_data = ache_properties.get("header_box", {})
            if header_data:
                issues.extend(self._check_header_box(header_data))

            # Fan system checks
            fan_data = ache_properties.get("fan_system", {})
            if fan_data:
                issues.extend(self._check_fan_system(fan_data))

            # Structural checks
            structural_data = ache_properties.get("structural", {})
            if structural_data:
                issues.extend(self._check_structural(structural_data))

            # Access provisions checks
            access_data = ache_properties.get("access", {})
            if access_data:
                issues.extend(self._check_access(access_data))

            # Compile report
            report.issues = issues
            report.total_checks = len(issues)
            report.passed = sum(1 for i in issues if i.status == ComplianceStatus.COMPLIANT)
            report.failed = sum(1 for i in issues if i.status == ComplianceStatus.NON_COMPLIANT)
            report.warnings = sum(1 for i in issues if i.status == ComplianceStatus.WARNING)
            report.is_compliant = report.failed == 0

            # Generate summary
            if report.is_compliant:
                if report.warnings > 0:
                    report.summary = f"Design is API 661 compliant with {report.warnings} warnings"
                else:
                    report.summary = "Design is fully API 661 compliant"
            else:
                report.summary = f"Design has {report.failed} non-compliant items requiring attention"

            logger.info(f"Compliance check: {report.passed}/{report.total_checks} passed")

        except Exception as e:
            logger.error(f"Compliance check error: {e}")
            report.summary = f"Error during compliance check: {e}"

        return report

    def _check_tube_bundle(self, data: Dict) -> List[ComplianceIssue]:
        """Check tube bundle requirements."""
        issues = []
        reqs = self._kb.API_661_REQUIREMENTS["tube_bundle"]

        # Tube length
        tube_length = data.get("tube_length_m", 0)
        if tube_length > 0:
            status = ComplianceStatus.COMPLIANT if tube_length <= reqs["max_tube_length_m"] else ComplianceStatus.NON_COMPLIANT
            issues.append(ComplianceIssue(
                code_reference="API 661 5.1.1",
                requirement=f"Maximum tube length: {reqs['max_tube_length_m']}m",
                actual_value=f"{tube_length}m",
                required_value=f"<= {reqs['max_tube_length_m']}m",
                status=status,
                severity="high" if status == ComplianceStatus.NON_COMPLIANT else "low",
                recommendation="Consider shorter tubes or multiple bays" if status == ComplianceStatus.NON_COMPLIANT else "",
            ))

        # Tube OD
        tube_od = data.get("tube_od_mm", 0)
        if tube_od > 0:
            in_range = reqs["min_tube_od_mm"] <= tube_od <= reqs["max_tube_od_mm"]
            status = ComplianceStatus.COMPLIANT if in_range else ComplianceStatus.WARNING
            issues.append(ComplianceIssue(
                code_reference="API 661 5.1.2",
                requirement=f"Tube OD: {reqs['min_tube_od_mm']}-{reqs['max_tube_od_mm']}mm",
                actual_value=f"{tube_od}mm",
                required_value=f"{reqs['min_tube_od_mm']}-{reqs['max_tube_od_mm']}mm",
                status=status,
                severity="medium" if status == ComplianceStatus.WARNING else "low",
            ))

        # Tube wall thickness
        tube_wall = data.get("tube_wall_mm", 0)
        if tube_wall > 0:
            status = ComplianceStatus.COMPLIANT if tube_wall >= reqs["min_tube_wall_mm"] else ComplianceStatus.NON_COMPLIANT
            issues.append(ComplianceIssue(
                code_reference="API 661 5.1.3",
                requirement=f"Minimum tube wall: {reqs['min_tube_wall_mm']}mm (BWG 14)",
                actual_value=f"{tube_wall}mm",
                required_value=f">= {reqs['min_tube_wall_mm']}mm",
                status=status,
                severity="high" if status == ComplianceStatus.NON_COMPLIANT else "low",
                recommendation="Increase tube wall thickness" if status == ComplianceStatus.NON_COMPLIANT else "",
            ))

        return issues

    def _check_header_box(self, data: Dict) -> List[ComplianceIssue]:
        """Check header box requirements."""
        issues = []
        reqs = self._kb.API_661_REQUIREMENTS["header_box"]

        # Minimum thickness
        thickness = data.get("wall_thickness_mm", 0)
        if thickness > 0:
            status = ComplianceStatus.COMPLIANT if thickness >= reqs["min_thickness_mm"] else ComplianceStatus.NON_COMPLIANT
            issues.append(ComplianceIssue(
                code_reference="API 661 5.2.1",
                requirement=f"Minimum header thickness: {reqs['min_thickness_mm']}mm",
                actual_value=f"{thickness}mm",
                required_value=f">= {reqs['min_thickness_mm']}mm",
                status=status,
                severity="critical" if status == ComplianceStatus.NON_COMPLIANT else "low",
            ))

        # Corrosion allowance
        ca = data.get("corrosion_allowance_mm", 0)
        status = ComplianceStatus.COMPLIANT if ca >= reqs["min_corrosion_allowance_mm"] else ComplianceStatus.WARNING
        issues.append(ComplianceIssue(
            code_reference="API 661 5.2.2",
            requirement=f"Minimum corrosion allowance: {reqs['min_corrosion_allowance_mm']}mm",
            actual_value=f"{ca}mm",
            required_value=f">= {reqs['min_corrosion_allowance_mm']}mm",
            status=status,
            severity="medium",
            recommendation="Consider increasing corrosion allowance for longevity",
        ))

        return issues

    def _check_fan_system(self, data: Dict) -> List[ComplianceIssue]:
        """Check fan system requirements."""
        issues = []
        reqs = self._kb.API_661_REQUIREMENTS["fan"]

        # Tip speed
        tip_speed = data.get("tip_speed_m_s", 0)
        if tip_speed > 0:
            status = ComplianceStatus.COMPLIANT if tip_speed <= reqs["max_tip_speed_m_s"] else ComplianceStatus.NON_COMPLIANT
            issues.append(ComplianceIssue(
                code_reference="API 661 6.1.1",
                requirement=f"Maximum tip speed: {reqs['max_tip_speed_m_s']} m/s",
                actual_value=f"{tip_speed:.1f} m/s",
                required_value=f"<= {reqs['max_tip_speed_m_s']} m/s",
                status=status,
                severity="high" if status == ComplianceStatus.NON_COMPLIANT else "low",
                recommendation="Reduce fan speed or increase fan diameter" if status == ComplianceStatus.NON_COMPLIANT else "",
            ))

        # Blade clearance
        clearance = data.get("blade_clearance_mm", 0)
        if clearance > 0:
            status = ComplianceStatus.COMPLIANT if clearance >= reqs["min_blade_clearance_mm"] else ComplianceStatus.NON_COMPLIANT
            issues.append(ComplianceIssue(
                code_reference="API 661 6.1.2",
                requirement=f"Minimum blade clearance: {reqs['min_blade_clearance_mm']}mm",
                actual_value=f"{clearance}mm",
                required_value=f">= {reqs['min_blade_clearance_mm']}mm",
                status=status,
                severity="medium",
            ))

        return issues

    def _check_structural(self, data: Dict) -> List[ComplianceIssue]:
        """Check structural requirements."""
        issues = []
        # Structural checks would be added here
        return issues

    def _check_access(self, data: Dict) -> List[ComplianceIssue]:
        """Check access provision requirements."""
        issues = []
        reqs = self._kb.API_661_REQUIREMENTS["access"]

        # Walkway width
        walkway_width = data.get("walkway_width_mm", 0)
        if walkway_width > 0:
            status = ComplianceStatus.COMPLIANT if walkway_width >= reqs["min_walkway_width_mm"] else ComplianceStatus.NON_COMPLIANT
            issues.append(ComplianceIssue(
                code_reference="API 661 7.1 / OSHA",
                requirement=f"Minimum walkway width: {reqs['min_walkway_width_mm']}mm",
                actual_value=f"{walkway_width}mm",
                required_value=f">= {reqs['min_walkway_width_mm']}mm",
                status=status,
                severity="high" if status == ComplianceStatus.NON_COMPLIANT else "low",
            ))

        # Handrail height
        handrail_height = data.get("handrail_height_mm", 0)
        if handrail_height > 0:
            status = ComplianceStatus.COMPLIANT if handrail_height >= reqs["handrail_height_mm"] else ComplianceStatus.NON_COMPLIANT
            issues.append(ComplianceIssue(
                code_reference="OSHA 1910.29",
                requirement=f"Minimum handrail height: {reqs['handrail_height_mm']}mm",
                actual_value=f"{handrail_height}mm",
                required_value=f">= {reqs['handrail_height_mm']}mm",
                status=status,
                severity="high" if status == ComplianceStatus.NON_COMPLIANT else "low",
            ))

        return issues

    def get_design_recommendations(
        self,
        ache_properties: Dict[str, Any],
        focus_area: Optional[str] = None,
    ) -> List[DesignRecommendation]:
        """
        Generate design recommendations based on ACHE properties.

        Args:
            ache_properties: Extracted ACHE properties
            focus_area: Specific area to focus on (optional)

        Returns:
            List of DesignRecommendation
        """
        recommendations = []

        try:
            # Thermal design recommendations
            if focus_area is None or focus_area == "thermal":
                thermal_recs = self._get_thermal_recommendations(ache_properties)
                recommendations.extend(thermal_recs)

            # Mechanical recommendations
            if focus_area is None or focus_area == "mechanical":
                mech_recs = self._get_mechanical_recommendations(ache_properties)
                recommendations.extend(mech_recs)

            # Fan system recommendations
            if focus_area is None or focus_area == "fan":
                fan_recs = self._get_fan_recommendations(ache_properties)
                recommendations.extend(fan_recs)

            logger.info(f"Generated {len(recommendations)} recommendations")

        except Exception as e:
            logger.error(f"Recommendation generation error: {e}")

        return recommendations

    def _get_thermal_recommendations(self, props: Dict) -> List[DesignRecommendation]:
        """Generate thermal design recommendations."""
        recs = []

        tube_bundle = props.get("tube_bundle", {})
        thermal = props.get("thermal_performance", {})

        # Check approach temperature
        approach = thermal.get("approach_temp_c", 0)
        if approach < 10:
            recs.append(DesignRecommendation(
                category="Thermal Design",
                recommendation="Consider increasing approach temperature",
                rationale=f"Current approach of {approach}°C is below recommended 10°C minimum",
                impact="high",
                references=["API 661 Annex A"],
                alternatives=[
                    "Increase surface area",
                    "Add more tube rows",
                    "Use enhanced fins",
                ],
            ))

        # Check overdesign margin
        overdesign = thermal.get("overdesign_percent", 0)
        if overdesign < 10:
            recs.append(DesignRecommendation(
                category="Thermal Design",
                recommendation="Increase thermal overdesign margin",
                rationale=f"Current {overdesign}% overdesign provides limited margin for fouling",
                impact="medium",
                references=["API 661 5.1"],
            ))

        return recs

    def _get_mechanical_recommendations(self, props: Dict) -> List[DesignRecommendation]:
        """Generate mechanical design recommendations."""
        recs = []

        header = props.get("header_box", {})

        # Check pressure rating
        design_pressure = header.get("design_pressure_kpa", 0)
        if design_pressure > 2000:
            recs.append(DesignRecommendation(
                category="Mechanical Design",
                recommendation="Consider plug-type header for high pressure",
                rationale="Plug headers are more economical above 2 MPa design pressure",
                impact="medium",
                references=["API 661 5.2.3"],
                alternatives=["Cover plate header with high-strength bolting"],
            ))

        return recs

    def _get_fan_recommendations(self, props: Dict) -> List[DesignRecommendation]:
        """Generate fan system recommendations."""
        recs = []

        fan = props.get("fan_system", {})
        process = props.get("process", {})

        # Check for induced vs forced draft
        process_temp = process.get("inlet_temp_c", 0)
        draft_type = fan.get("draft_type", "")

        if process_temp > 150 and draft_type.lower() == "forced":
            recs.append(DesignRecommendation(
                category="Fan System",
                recommendation="Consider induced draft configuration",
                rationale="High process temperature (>150°C) may damage fan components in forced draft",
                impact="high",
                references=["API 661 6.1"],
                alternatives=["Add fan ring insulation", "Use high-temperature fan materials"],
            ))

        return recs

    def get_optimization_suggestions(
        self,
        ache_properties: Dict[str, Any],
        optimize_for: str = "cost",
    ) -> List[OptimizationSuggestion]:
        """
        Generate optimization suggestions.

        Args:
            ache_properties: ACHE properties
            optimize_for: Optimization target (cost, weight, performance, maintenance)

        Returns:
            List of OptimizationSuggestion
        """
        suggestions = []

        try:
            if optimize_for == "cost":
                suggestions.extend(self._cost_optimizations(ache_properties))
            elif optimize_for == "weight":
                suggestions.extend(self._weight_optimizations(ache_properties))
            elif optimize_for == "performance":
                suggestions.extend(self._performance_optimizations(ache_properties))
            elif optimize_for == "maintenance":
                suggestions.extend(self._maintenance_optimizations(ache_properties))

            logger.info(f"Generated {len(suggestions)} optimization suggestions for {optimize_for}")

        except Exception as e:
            logger.error(f"Optimization suggestion error: {e}")

        return suggestions

    def _cost_optimizations(self, props: Dict) -> List[OptimizationSuggestion]:
        """Generate cost optimization suggestions."""
        suggestions = []

        tube_bundle = props.get("tube_bundle", {})

        # Check for potential over-design
        overdesign = props.get("thermal_performance", {}).get("overdesign_percent", 0)
        if overdesign > 25:
            suggestions.append(OptimizationSuggestion(
                area="Tube Bundle",
                current_state=f"{overdesign}% thermal overdesign",
                suggested_change="Reduce number of tube rows",
                potential_benefit="Lower material and installation costs",
                estimated_savings={"material_percent": 10, "installation_percent": 5},
                implementation_effort="low",
            ))

        return suggestions

    def _weight_optimizations(self, props: Dict) -> List[OptimizationSuggestion]:
        """Generate weight optimization suggestions."""
        return []

    def _performance_optimizations(self, props: Dict) -> List[OptimizationSuggestion]:
        """Generate performance optimization suggestions."""
        return []

    def _maintenance_optimizations(self, props: Dict) -> List[OptimizationSuggestion]:
        """Generate maintenance optimization suggestions."""
        return []

    def troubleshoot(
        self,
        problem: str,
        ache_properties: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Provide troubleshooting guidance.

        Args:
            problem: Description of problem or problem key
            ache_properties: Current ACHE properties (optional)

        Returns:
            Dictionary with troubleshooting information
        """
        result = {
            "problem": problem,
            "possible_causes": [],
            "diagnostic_steps": [],
            "solutions": [],
            "references": [],
        }

        try:
            # Check if it's a known problem type
            problem_lower = problem.lower()

            if "temperature" in problem_lower or "hot" in problem_lower:
                guide = self._kb.TROUBLESHOOTING_GUIDES.get("high_process_outlet_temp", {})
            elif "vibration" in problem_lower:
                guide = self._kb.TROUBLESHOOTING_GUIDES.get("excessive_vibration", {})
            elif "leak" in problem_lower:
                guide = self._kb.TROUBLESHOOTING_GUIDES.get("tube_leaks", {})
            else:
                guide = {}

            if guide:
                result["possible_causes"] = guide.get("possible_causes", [])
                result["diagnostic_steps"] = guide.get("diagnostic_steps", [])
                result["solutions"] = guide.get("solutions", [])
                result["references"] = ["API 661", "Equipment manufacturer documentation"]
            else:
                result["message"] = "No specific troubleshooting guide available. Consider consulting equipment documentation."

            logger.info(f"Troubleshooting for: {problem}")

        except Exception as e:
            logger.error(f"Troubleshooting error: {e}")
            result["error"] = str(e)

        return result

    def query_knowledge_base(
        self,
        query: str,
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Query the ACHE knowledge base.

        Args:
            query: Query string
            category: Optional category to search

        Returns:
            Dictionary with relevant information
        """
        result = {
            "query": query,
            "results": [],
            "references": [],
        }

        try:
            query_lower = query.lower()

            # Search design guidelines
            for cat, guidelines in self._kb.DESIGN_GUIDELINES.items():
                if category and cat != category:
                    continue

                for guideline in guidelines:
                    if any(word in guideline.lower() for word in query_lower.split()):
                        result["results"].append({
                            "category": cat,
                            "guideline": guideline,
                        })

            # Search API 661 requirements
            for section, reqs in self._kb.API_661_REQUIREMENTS.items():
                if category and section != category:
                    continue

                section_text = json.dumps(reqs)
                if any(word in section_text.lower() for word in query_lower.split()):
                    result["results"].append({
                        "category": f"API 661 - {section}",
                        "requirements": reqs,
                    })

            result["references"] = ["API 661 / ISO 13706", "ASME Section VIII"]
            logger.info(f"Knowledge query: {query}, found {len(result['results'])} results")

        except Exception as e:
            logger.error(f"Knowledge query error: {e}")
            result["error"] = str(e)

        return result

    def generate_report_summary(
        self,
        ache_properties: Dict[str, Any],
        compliance_report: Optional[ComplianceReport] = None,
    ) -> str:
        """
        Generate a summary report of ACHE design.

        Args:
            ache_properties: ACHE properties
            compliance_report: Optional compliance report

        Returns:
            Formatted summary string
        """
        lines = []
        lines.append("=" * 60)
        lines.append("ACHE DESIGN SUMMARY REPORT")
        lines.append("=" * 60)

        # Basic info
        lines.append(f"\nUnit Tag: {ache_properties.get('unit_tag', 'N/A')}")
        lines.append(f"Service: {ache_properties.get('service', 'N/A')}")

        # Tube bundle
        tube = ache_properties.get("tube_bundle", {})
        if tube:
            lines.append("\n--- Tube Bundle ---")
            lines.append(f"Tubes: {tube.get('num_tubes', 'N/A')} x {tube.get('tube_length_m', 'N/A')}m")
            lines.append(f"Tube OD: {tube.get('tube_od_mm', 'N/A')}mm")
            lines.append(f"Rows: {tube.get('num_rows', 'N/A')}")

        # Fan system
        fan = ache_properties.get("fan_system", {})
        if fan:
            lines.append("\n--- Fan System ---")
            lines.append(f"Fans: {fan.get('num_fans', 'N/A')}")
            lines.append(f"Diameter: {fan.get('diameter_m', 'N/A')}m")
            lines.append(f"Motor: {fan.get('motor_kw', 'N/A')} kW")

        # Compliance
        if compliance_report:
            lines.append("\n--- API 661 Compliance ---")
            lines.append(f"Status: {'COMPLIANT' if compliance_report.is_compliant else 'NON-COMPLIANT'}")
            lines.append(f"Checks: {compliance_report.passed}/{compliance_report.total_checks} passed")
            if compliance_report.failed > 0:
                lines.append(f"Issues: {compliance_report.failed} require attention")

        lines.append("\n" + "=" * 60)

        return "\n".join(lines)
