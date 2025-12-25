"""
Rules Engine - Central coordinator for rule enforcement

Provides:
- Context-aware rule retrieval
- System prompt generation
- Rule-based decision making
- Integration with agents and chatbot
"""

from pathlib import Path
from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import json

from .parser import RulesParser, Rule, Section, get_rules_parser


@dataclass
class RuleContext:
    """Context for rule evaluation."""

    agent_type: str
    user_message: str
    task_type: Optional[str] = None
    relevant_files: List[str] = None
    current_action: Optional[str] = None

    def __post_init__(self):
        if self.relevant_files is None:
            self.relevant_files = []


@dataclass
class RuleCheck:
    """Result of a rule check."""

    rule: Rule
    passed: bool
    message: str
    severity: str = "warning"  # info, warning, error, blocker


class RulesEngine:
    """
    Central rules engine for Project Vulcan.

    Responsibilities:
    - Load and cache RULES.md
    - Generate context-aware system prompts
    - Validate actions against rules
    - Provide rule-based guidance
    """

    def __init__(self, rules_path: Optional[Path] = None):
        """Initialize rules engine."""
        self.parser = RulesParser(rules_path) if rules_path else get_rules_parser()
        self._loaded = False
        self._last_load: Optional[datetime] = None

        # Rule check callbacks
        self._pre_action_checks: List[Callable[[RuleContext], List[RuleCheck]]] = []
        self._post_action_checks: List[Callable[[RuleContext, Any], List[RuleCheck]]] = []

    def load(self, force: bool = False) -> None:
        """Load and parse rules."""
        self.parser.parse(force=force)
        self._loaded = True
        self._last_load = datetime.now()

    def ensure_loaded(self) -> None:
        """Ensure rules are loaded."""
        if not self._loaded:
            self.load()

    # =========================================================================
    # System Prompt Generation
    # =========================================================================

    def get_system_prompt(
        self,
        agent_type: str,
        include_sections: Optional[List[int]] = None,
        context: Optional[str] = None,
        max_tokens: int = 4000
    ) -> str:
        """
        Generate a system prompt with relevant rules for an agent.

        Args:
            agent_type: Type of agent (cad, trading, work, etc.)
            include_sections: Specific sections to include
            context: Additional context for rule matching
            max_tokens: Maximum tokens for rules portion

        Returns:
            Formatted system prompt with rules
        """
        self.ensure_loaded()

        # Build prompt header
        prompt_parts = [
            "# RULES & GUIDELINES",
            "",
            "You MUST follow these rules from RULES.md. Violations are not acceptable.",
            "",
        ]

        # Add critical rules first (always)
        critical_rules = self.parser.get_critical_rules()
        if critical_rules:
            prompt_parts.append("## CRITICAL RULES (Absolute Requirements)")
            prompt_parts.append("")
            for rule in critical_rules[:5]:  # Top 5 critical
                prompt_parts.append(f"**Rule {rule.number}: {rule.name}**")
                # Truncate content for prompt
                content = rule.content[:500] + "..." if len(rule.content) > 500 else rule.content
                prompt_parts.append(content)
                prompt_parts.append("")

        # Add agent-specific rules
        agent_rules = self.parser.get_rules_for_agent(agent_type)
        if agent_rules:
            prompt_parts.append(f"## {agent_type.upper()} Agent Rules")
            prompt_parts.append("")
            for rule in agent_rules[:10]:  # Top 10 for agent
                if rule.priority == "critical":
                    continue  # Already added above
                prompt_parts.append(f"**Rule {rule.number}: {rule.name}**")
                content = rule.content[:300] + "..." if len(rule.content) > 300 else rule.content
                prompt_parts.append(content)
                prompt_parts.append("")

        # Add section-specific rules if requested
        if include_sections:
            for section_num in include_sections:
                section = self.parser.get_section(section_num)
                if section:
                    prompt_parts.append(f"## Section {section.number}: {section.name}")
                    prompt_parts.append("")
                    for rule in section.rules[:5]:  # Top 5 per section
                        prompt_parts.append(f"**Rule {rule.number}: {rule.name}**")
                        content = rule.content[:300] + "..." if len(rule.content) > 300 else rule.content
                        prompt_parts.append(content)
                        prompt_parts.append("")

        # Add context-matched rules
        if context:
            matched_rules = self.parser.search_rules(context)
            if matched_rules:
                prompt_parts.append("## Context-Relevant Rules")
                prompt_parts.append("")
                for rule in matched_rules[:3]:  # Top 3 matched
                    prompt_parts.append(f"**Rule {rule.number}: {rule.name}**")
                    content = rule.content[:300] + "..." if len(rule.content) > 300 else rule.content
                    prompt_parts.append(content)
                    prompt_parts.append("")

        # Add acknowledgment requirement
        prompt_parts.append("---")
        prompt_parts.append("**ACKNOWLEDGMENT**: Before starting any task, state: 'Checked RULES.md - relevant sections: [X, Y, Z]'")
        prompt_parts.append("")

        return "\n".join(prompt_parts)

    def get_cad_system_prompt(self, task_description: Optional[str] = None) -> str:
        """Generate system prompt specifically for CAD agent."""
        # Always include sections 0, 7, 10 for CAD
        return self.get_system_prompt(
            agent_type="cad",
            include_sections=[0, 7, 10],
            context=task_description
        )

    def get_trading_system_prompt(self, task_description: Optional[str] = None) -> str:
        """Generate system prompt for trading agent."""
        return self.get_system_prompt(
            agent_type="trading",
            context=task_description
        )

    # =========================================================================
    # Rule Validation
    # =========================================================================

    def check_action(self, context: RuleContext) -> List[RuleCheck]:
        """
        Check if an action violates any rules.

        Args:
            context: The context of the action being taken

        Returns:
            List of rule check results
        """
        self.ensure_loaded()
        checks: List[RuleCheck] = []

        # Get relevant rules
        agent_rules = self.parser.get_rules_for_agent(context.agent_type)
        context_rules = self.parser.search_rules(context.user_message)

        all_relevant = set(agent_rules + context_rules)

        # CAD-specific checks
        if context.agent_type == "cad":
            checks.extend(self._check_cad_rules(context))

        # Run registered pre-action checks
        for check_fn in self._pre_action_checks:
            try:
                checks.extend(check_fn(context))
            except Exception as e:
                checks.append(RuleCheck(
                    rule=Rule(0, "Check Error", str(e), "System"),
                    passed=False,
                    message=f"Rule check failed: {e}",
                    severity="warning"
                ))

        return checks

    def _check_cad_rules(self, context: RuleContext) -> List[RuleCheck]:
        """CAD-specific rule checks."""
        checks = []
        msg_lower = context.user_message.lower()

        # Check for plan requirement (Rule 32)
        if any(word in msg_lower for word in ["build", "create", "model", "design", "make"]):
            rule32 = self.parser.get_rule(32)
            if rule32:
                checks.append(RuleCheck(
                    rule=rule32,
                    passed=False,
                    message="CAD build requested. A PLAN file must be created and approved before proceeding.",
                    severity="blocker"
                ))

        # Check for data sourcing (Rule 35)
        if any(word in msg_lower for word in ["flange", "pipe", "fitting", "bolt"]):
            rule35 = self.parser.get_rule(35)
            if rule35:
                checks.append(RuleCheck(
                    rule=rule35,
                    passed=True,  # Just a reminder
                    message="Standard part detected. Ensure dimensions come from verified sources (local JSON, fluids package, or user-provided).",
                    severity="info"
                ))

        return checks

    def get_blockers(self, checks: List[RuleCheck]) -> List[RuleCheck]:
        """Get only blocking rule violations."""
        return [c for c in checks if c.severity == "blocker" and not c.passed]

    def get_warnings(self, checks: List[RuleCheck]) -> List[RuleCheck]:
        """Get only warning-level rule issues."""
        return [c for c in checks if c.severity == "warning" and not c.passed]

    # =========================================================================
    # Rule Lookup
    # =========================================================================

    def get_rule(self, rule_num: int) -> Optional[Rule]:
        """Get a specific rule by number."""
        self.ensure_loaded()
        return self.parser.get_rule(rule_num)

    def get_section(self, section_num: int) -> Optional[Section]:
        """Get a specific section by number."""
        self.ensure_loaded()
        return self.parser.get_section(section_num)

    def search(self, query: str) -> List[Rule]:
        """Search rules by keyword."""
        self.ensure_loaded()
        return self.parser.search_rules(query)

    # =========================================================================
    # Registration
    # =========================================================================

    def register_pre_action_check(
        self,
        check_fn: Callable[[RuleContext], List[RuleCheck]]
    ) -> None:
        """Register a custom pre-action rule check."""
        self._pre_action_checks.append(check_fn)

    def register_post_action_check(
        self,
        check_fn: Callable[[RuleContext, Any], List[RuleCheck]]
    ) -> None:
        """Register a custom post-action rule check."""
        self._post_action_checks.append(check_fn)

    # =========================================================================
    # Utilities
    # =========================================================================

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of loaded rules."""
        self.ensure_loaded()
        summary = self.parser.get_summary()
        summary["last_load"] = self._last_load.isoformat() if self._last_load else None
        return summary

    def format_rule_for_display(self, rule: Rule) -> str:
        """Format a rule for user display."""
        priority_badge = ""
        if rule.priority == "critical":
            priority_badge = "[CRITICAL] "
        elif rule.priority == "high":
            priority_badge = "[IMPORTANT] "

        return f"""
{priority_badge}Rule {rule.number}: {rule.name}
Section: {rule.section}
Priority: {rule.priority}

{rule.content[:1000]}{"..." if len(rule.content) > 1000 else ""}
"""


# Singleton instance
_engine_instance: Optional[RulesEngine] = None


def get_rules_engine() -> RulesEngine:
    """Get singleton rules engine instance."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = RulesEngine()
    return _engine_instance
