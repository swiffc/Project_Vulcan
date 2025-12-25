"""
Rule Validator - Enforces rules during agent execution

Provides:
- Pre-action validation
- Post-action validation
- Constraint checking
- Violation reporting
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime
from pathlib import Path
import re
import json

from .parser import Rule
from .engine import RulesEngine, RuleContext, RuleCheck, get_rules_engine


@dataclass
class ValidationResult:
    """Result of a validation check."""

    valid: bool
    blockers: List[RuleCheck] = field(default_factory=list)
    warnings: List[RuleCheck] = field(default_factory=list)
    info: List[RuleCheck] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def can_proceed(self) -> bool:
        """Check if action can proceed (no blockers)."""
        return len(self.blockers) == 0

    def to_message(self) -> str:
        """Format validation result as user message."""
        if self.valid and self.can_proceed:
            if self.warnings:
                return f"Validation passed with {len(self.warnings)} warning(s)."
            return "Validation passed."

        parts = []
        if self.blockers:
            parts.append("**BLOCKED** - Cannot proceed:")
            for check in self.blockers:
                parts.append(f"  - Rule {check.rule.number}: {check.message}")

        if self.warnings:
            parts.append("\nWarnings:")
            for check in self.warnings:
                parts.append(f"  - Rule {check.rule.number}: {check.message}")

        return "\n".join(parts)


class RuleValidator:
    """
    Validates actions against RULES.md.

    Features:
    - CAD-specific validation (plan requirement, data sources)
    - Trading-specific validation
    - Custom validation rules
    - Violation history tracking
    """

    def __init__(self, engine: Optional[RulesEngine] = None):
        """Initialize validator with rules engine."""
        self.engine = engine or get_rules_engine()
        self.violation_history: List[Dict[str, Any]] = []

        # Custom validators by agent type
        self._custom_validators: Dict[str, List[Callable]] = {
            "cad": [],
            "trading": [],
            "work": [],
            "general": []
        }

    def validate(self, context: RuleContext) -> ValidationResult:
        """
        Validate an action against all applicable rules.

        Args:
            context: The context of the action

        Returns:
            ValidationResult with pass/fail and details
        """
        all_checks: List[RuleCheck] = []

        # Run engine checks
        all_checks.extend(self.engine.check_action(context))

        # Run agent-specific validators
        if context.agent_type in self._custom_validators:
            for validator in self._custom_validators[context.agent_type]:
                try:
                    all_checks.extend(validator(context))
                except Exception as e:
                    all_checks.append(RuleCheck(
                        rule=Rule(0, "Validator Error", str(e), "System"),
                        passed=False,
                        message=f"Custom validator failed: {e}",
                        severity="warning"
                    ))

        # Categorize checks
        blockers = [c for c in all_checks if c.severity == "blocker" and not c.passed]
        warnings = [c for c in all_checks if c.severity == "warning" and not c.passed]
        info = [c for c in all_checks if c.severity == "info"]

        result = ValidationResult(
            valid=len(blockers) == 0,
            blockers=blockers,
            warnings=warnings,
            info=info
        )

        # Track violations
        if blockers or warnings:
            self._record_violation(context, result)

        return result

    def validate_cad_build(
        self,
        task: str,
        has_plan: bool = False,
        plan_approved: bool = False,
        data_sources: Optional[List[str]] = None
    ) -> ValidationResult:
        """
        Validate a CAD build request.

        Args:
            task: Description of the build task
            has_plan: Whether a plan file exists
            plan_approved: Whether the plan was approved by user
            data_sources: List of data sources used

        Returns:
            ValidationResult
        """
        context = RuleContext(
            agent_type="cad",
            user_message=task,
            task_type="build"
        )

        checks: List[RuleCheck] = []

        # Rule 32: No Build Without Approved Plan
        rule32 = self.engine.get_rule(32)
        if rule32:
            if not has_plan:
                checks.append(RuleCheck(
                    rule=rule32,
                    passed=False,
                    message="No PLAN file exists. Create output/PLAN_{part_name}.md before building.",
                    severity="blocker"
                ))
            elif not plan_approved:
                checks.append(RuleCheck(
                    rule=rule32,
                    passed=False,
                    message="PLAN exists but not approved. Wait for user approval before building.",
                    severity="blocker"
                ))
            else:
                checks.append(RuleCheck(
                    rule=rule32,
                    passed=True,
                    message="PLAN exists and is approved.",
                    severity="info"
                ))

        # Rule 35: Data Sourcing Hierarchy
        rule35 = self.engine.get_rule(35)
        if rule35 and data_sources:
            valid_sources = ["pipe_schedules.json", "engineering_standards.json", "fluids.piping", "user-provided"]
            invalid_sources = [s for s in data_sources if not any(v in s for v in valid_sources)]

            if invalid_sources:
                checks.append(RuleCheck(
                    rule=rule35,
                    passed=False,
                    message=f"Invalid data sources detected: {invalid_sources}. Use verified sources only.",
                    severity="warning"
                ))

        # Categorize
        blockers = [c for c in checks if c.severity == "blocker" and not c.passed]
        warnings = [c for c in checks if c.severity == "warning" and not c.passed]
        info = [c for c in checks if c.severity == "info"]

        return ValidationResult(
            valid=len(blockers) == 0,
            blockers=blockers,
            warnings=warnings,
            info=info
        )

    def validate_plan_structure(self, plan_content: str) -> ValidationResult:
        """
        Validate that a PLAN file has all required sections.

        Args:
            plan_content: Content of the plan file

        Returns:
            ValidationResult
        """
        checks: List[RuleCheck] = []

        # Rule 34: Plan Structure Template
        rule34 = self.engine.get_rule(34)
        if rule34:
            required_phases = [
                "PHASE 1: IDENTIFY",
                "PHASE 2: CLASSIFY",
                "PHASE 3: DECOMPOSE",
                "PHASE 4: DATA SOURCING",
                "PHASE 5: BUILD STRATEGY",
                "PHASE 6: API SEQUENCE",
                "PHASE 7: VALIDATION"
            ]

            missing_phases = []
            for phase in required_phases:
                if phase not in plan_content:
                    missing_phases.append(phase)

            if missing_phases:
                checks.append(RuleCheck(
                    rule=rule34,
                    passed=False,
                    message=f"Plan missing required phases: {missing_phases}",
                    severity="blocker"
                ))
            else:
                checks.append(RuleCheck(
                    rule=rule34,
                    passed=True,
                    message="Plan has all required phases.",
                    severity="info"
                ))

        # Check for verification markers (Rule 38)
        rule38 = self.engine.get_rule(38)
        if rule38:
            has_verified = "VERIFIED" in plan_content or "verified" in plan_content
            has_not_found = "NOT FOUND" in plan_content or "NOT_FOUND" in plan_content

            if has_not_found:
                checks.append(RuleCheck(
                    rule=rule38,
                    passed=False,
                    message="Plan contains unresolved 'NOT FOUND' dimensions. Cannot proceed until resolved.",
                    severity="blocker"
                ))

            if not has_verified:
                checks.append(RuleCheck(
                    rule=rule38,
                    passed=False,
                    message="No dimensions marked as VERIFIED. Add source citations.",
                    severity="warning"
                ))

        # Categorize
        blockers = [c for c in checks if c.severity == "blocker" and not c.passed]
        warnings = [c for c in checks if c.severity == "warning" and not c.passed]
        info = [c for c in checks if c.severity == "info"]

        return ValidationResult(
            valid=len(blockers) == 0,
            blockers=blockers,
            warnings=warnings,
            info=info
        )

    def _record_violation(self, context: RuleContext, result: ValidationResult) -> None:
        """Record a rule violation for history tracking."""
        self.violation_history.append({
            "timestamp": datetime.now().isoformat(),
            "agent_type": context.agent_type,
            "task_type": context.task_type,
            "message": context.user_message[:200],
            "blockers": [{"rule": c.rule.number, "message": c.message} for c in result.blockers],
            "warnings": [{"rule": c.rule.number, "message": c.message} for c in result.warnings]
        })

        # Keep only last 100 violations
        if len(self.violation_history) > 100:
            self.violation_history = self.violation_history[-100:]

    def register_validator(
        self,
        agent_type: str,
        validator_fn: Callable[[RuleContext], List[RuleCheck]]
    ) -> None:
        """Register a custom validator for an agent type."""
        if agent_type not in self._custom_validators:
            self._custom_validators[agent_type] = []
        self._custom_validators[agent_type].append(validator_fn)

    def get_violation_summary(self) -> Dict[str, Any]:
        """Get summary of recent violations."""
        if not self.violation_history:
            return {"total": 0, "by_rule": {}, "by_agent": {}}

        by_rule: Dict[int, int] = {}
        by_agent: Dict[str, int] = {}

        for violation in self.violation_history:
            agent = violation.get("agent_type", "unknown")
            by_agent[agent] = by_agent.get(agent, 0) + 1

            for blocker in violation.get("blockers", []):
                rule_num = blocker.get("rule", 0)
                by_rule[rule_num] = by_rule.get(rule_num, 0) + 1

        return {
            "total": len(self.violation_history),
            "by_rule": by_rule,
            "by_agent": by_agent,
            "recent": self.violation_history[-5:]
        }


# Singleton
_validator_instance: Optional[RuleValidator] = None


def get_rule_validator() -> RuleValidator:
    """Get singleton rule validator instance."""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = RuleValidator()
    return _validator_instance
