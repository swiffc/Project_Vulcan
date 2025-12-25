"""
Design Recommender Agent
========================
Analyzes CAD models and provides AI-powered design recommendations.

Phase 24.10 Implementation
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("vulcan.agent.design_recommender")


class IssueSeverity(Enum):
    """Severity levels for design issues."""
    CRITICAL = "critical"  # Must fix before manufacturing
    WARNING = "warning"  # Should review
    SUGGESTION = "suggestion"  # Nice to have


@dataclass
class DesignIssue:
    """A design issue or recommendation."""
    severity: IssueSeverity
    category: str  # weight, cost, dfm, standards
    title: str
    description: str
    location: str = ""
    fix_action: Optional[str] = None  # Action to apply fix
    savings_estimate: Optional[str] = None


@dataclass
class RecommendationResult:
    """Complete recommendation analysis."""
    critical_issues: List[DesignIssue] = field(default_factory=list)
    warnings: List[DesignIssue] = field(default_factory=list)
    suggestions: List[DesignIssue] = field(default_factory=list)
    weight_savings_kg: float = 0.0
    cost_savings_pct: float = 0.0
    summary: str = ""


class DesignRecommender:
    """
    AI-powered design recommendation agent.
    Analyzes models for weight, cost, manufacturability, and standards compliance.
    """

    def __init__(self):
        self._llm = None

    def _get_llm(self):
        """Lazy load LLM client."""
        if self._llm is None:
            try:
                from core.llm import llm
                self._llm = llm
            except ImportError:
                logger.warning("LLM not available for recommendations")
        return self._llm

    def analyze_weight(self, model_data: Dict[str, Any]) -> List[DesignIssue]:
        """Analyze model for weight optimization opportunities."""
        issues = []

        mass_kg = model_data.get("mass_properties", {}).get("mass_kg", 0)
        if mass_kg > 1000:  # Heavy component
            issues.append(DesignIssue(
                severity=IssueSeverity.SUGGESTION,
                category="weight",
                title="Heavy Component",
                description=f"Component weighs {mass_kg:.1f} kg. Consider weight optimization.",
                savings_estimate=f"Potential 10-20% reduction ({mass_kg * 0.15:.1f} kg)",
            ))

        return issues

    def analyze_cost(self, model_data: Dict[str, Any]) -> List[DesignIssue]:
        """Analyze model for cost reduction opportunities."""
        issues = []

        # Check for exotic materials
        material = model_data.get("material", "").lower()
        if "inconel" in material or "hastelloy" in material or "titanium" in material:
            issues.append(DesignIssue(
                severity=IssueSeverity.WARNING,
                category="cost",
                title="Exotic Material",
                description=f"Using {material}. Verify if required by design conditions.",
                savings_estimate="30-50% if alternate material acceptable",
            ))

        return issues

    def analyze_dfm(self, model_data: Dict[str, Any]) -> List[DesignIssue]:
        """Analyze Design for Manufacturability."""
        issues = []

        # Check hole analysis
        hole_data = model_data.get("hole_analysis", {})
        ligament_violations = hole_data.get("ligament_violations", [])

        for violation in ligament_violations:
            issues.append(DesignIssue(
                severity=IssueSeverity.CRITICAL,
                category="dfm",
                title="Insufficient Ligament",
                description=f"Ligament between {violation.get('hole1')} and {violation.get('hole2')} "
                           f"is {violation.get('actual_ligament', 0) * 1000:.2f}mm, "
                           f"minimum required: {violation.get('required_ligament', 0) * 1000:.2f}mm",
                location=violation.get("hole1", ""),
                fix_action="Increase hole spacing or reduce hole diameter",
            ))

        # Check bend analysis
        bend_data = model_data.get("bend_analysis", {})
        bend_violations = bend_data.get("violations", [])

        for violation in bend_violations:
            issues.append(DesignIssue(
                severity=IssueSeverity.CRITICAL,
                category="dfm",
                title="Bend Radius Too Small",
                description=f"Bend {violation.get('name')} has radius "
                           f"{violation.get('actual_radius_m', 0) * 1000:.2f}mm, "
                           f"minimum for {violation.get('material')}: "
                           f"{violation.get('minimum_radius_m', 0) * 1000:.2f}mm",
                location=violation.get("name", ""),
                fix_action=f"Increase radius to {violation.get('suggested_radius_m', 0) * 1000:.2f}mm",
            ))

        return issues

    def analyze_standards(self, model_data: Dict[str, Any]) -> List[DesignIssue]:
        """Check standards compliance (API 661, ASME, TEMA)."""
        issues = []

        # This would integrate with existing validators
        custom_props = model_data.get("custom_properties", {})
        design_data = custom_props.get("design_data", {})

        # Check for missing critical properties
        required_props = ["pressure", "temperature"]
        for prop in required_props:
            found = any(prop.lower() in k.lower() for k in design_data.keys())
            if not found:
                issues.append(DesignIssue(
                    severity=IssueSeverity.WARNING,
                    category="standards",
                    title=f"Missing {prop.title()} Property",
                    description=f"Design {prop} not specified in custom properties.",
                ))

        return issues

    def get_recommendations(self, model_data: Dict[str, Any]) -> RecommendationResult:
        """Get all recommendations for a model."""
        result = RecommendationResult()

        # Run all analyzers
        all_issues = []
        all_issues.extend(self.analyze_weight(model_data))
        all_issues.extend(self.analyze_cost(model_data))
        all_issues.extend(self.analyze_dfm(model_data))
        all_issues.extend(self.analyze_standards(model_data))

        # Categorize by severity
        for issue in all_issues:
            if issue.severity == IssueSeverity.CRITICAL:
                result.critical_issues.append(issue)
            elif issue.severity == IssueSeverity.WARNING:
                result.warnings.append(issue)
            else:
                result.suggestions.append(issue)

        # Generate summary
        total = len(all_issues)
        critical = len(result.critical_issues)
        result.summary = (
            f"Found {total} issue(s): {critical} critical, "
            f"{len(result.warnings)} warnings, {len(result.suggestions)} suggestions."
        )

        return result

    def to_dict(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get recommendations as dictionary."""
        result = self.get_recommendations(model_data)

        def issue_to_dict(issue: DesignIssue) -> Dict:
            return {
                "severity": issue.severity.value,
                "category": issue.category,
                "title": issue.title,
                "description": issue.description,
                "location": issue.location,
                "fix_action": issue.fix_action,
                "savings_estimate": issue.savings_estimate,
            }

        return {
            "summary": result.summary,
            "critical_issues": [issue_to_dict(i) for i in result.critical_issues],
            "warnings": [issue_to_dict(i) for i in result.warnings],
            "suggestions": [issue_to_dict(i) for i in result.suggestions],
            "weight_savings_kg": result.weight_savings_kg,
            "cost_savings_pct": result.cost_savings_pct,
        }


# Singleton instance
_recommender: Optional[DesignRecommender] = None


def get_recommender() -> DesignRecommender:
    """Get the singleton recommender instance."""
    global _recommender
    if _recommender is None:
        _recommender = DesignRecommender()
    return _recommender
