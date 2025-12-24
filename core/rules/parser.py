"""
Rules Parser - Extracts structured rules from RULES.md

Parses markdown into sections, rules, and constraints.
Supports caching and incremental updates.
"""

import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import hashlib
import json


@dataclass
class Rule:
    """A single rule extracted from RULES.md."""

    number: int
    name: str
    content: str
    section: str
    keywords: List[str] = field(default_factory=list)
    priority: str = "normal"  # critical, high, normal, low
    applies_to: List[str] = field(default_factory=list)  # agent types

    def matches_context(self, context: str) -> bool:
        """Check if this rule is relevant to a given context."""
        context_lower = context.lower()
        return any(kw.lower() in context_lower for kw in self.keywords)

    def to_prompt_format(self) -> str:
        """Format rule for inclusion in system prompt."""
        priority_marker = ""
        if self.priority == "critical":
            priority_marker = "**[CRITICAL]** "
        elif self.priority == "high":
            priority_marker = "[IMPORTANT] "

        return f"{priority_marker}Rule {self.number}: {self.name}\n{self.content}"


@dataclass
class Section:
    """A section from RULES.md containing multiple rules."""

    number: int
    name: str
    description: str
    rules: List[Rule] = field(default_factory=list)
    subsections: List["Section"] = field(default_factory=list)

    def get_rules_for_agent(self, agent_type: str) -> List[Rule]:
        """Get rules that apply to a specific agent type."""
        matching = []
        for rule in self.rules:
            if not rule.applies_to or agent_type in rule.applies_to:
                matching.append(rule)
        return matching


class RulesParser:
    """
    Parses RULES.md into structured sections and rules.

    Features:
    - Caches parsed rules with file hash
    - Extracts keywords for rule matching
    - Identifies rule priority levels
    - Maps rules to agent types
    """

    # Agent type keywords for auto-detection
    AGENT_KEYWORDS = {
        "cad": ["cad", "solidworks", "inventor", "autocad", "flange", "part", "assembly", "asme", "drawing"],
        "trading": ["trade", "trading", "forex", "gbp", "ict", "btmm", "setup", "chart"],
        "work": ["work", "j2", "tracker", "excel", "outlook", "meeting", "task"],
        "sketch": ["sketch", "image", "vision", "photo", "ocr"],
        "general": []
    }

    # Priority keywords
    PRIORITY_MARKERS = {
        "critical": ["CRITICAL", "MANDATORY", "MUST", "ABSOLUTE", "NEVER", "ALWAYS"],
        "high": ["IMPORTANT", "REQUIRED", "SHOULD"],
        "low": ["optional", "may", "consider"]
    }

    def __init__(self, rules_path: Optional[Path] = None):
        """Initialize parser with path to RULES.md."""
        if rules_path is None:
            # Default to project root RULES.md
            self.rules_path = Path(__file__).parent.parent.parent / "RULES.md"
        else:
            self.rules_path = Path(rules_path)

        self._cache: Dict[str, Any] = {}
        self._file_hash: Optional[str] = None
        self.sections: List[Section] = []
        self.rules: List[Rule] = []

    def _get_file_hash(self) -> str:
        """Get MD5 hash of RULES.md for cache invalidation."""
        if not self.rules_path.exists():
            return ""
        content = self.rules_path.read_text(encoding="utf-8")
        return hashlib.md5(content.encode()).hexdigest()

    def parse(self, force: bool = False) -> List[Section]:
        """
        Parse RULES.md into sections and rules.

        Args:
            force: Force re-parse even if cached

        Returns:
            List of parsed sections
        """
        current_hash = self._get_file_hash()

        # Return cached if unchanged
        if not force and self._file_hash == current_hash and self.sections:
            return self.sections

        if not self.rules_path.exists():
            raise FileNotFoundError(f"RULES.md not found at {self.rules_path}")

        content = self.rules_path.read_text(encoding="utf-8")
        self._file_hash = current_hash

        # Parse content
        self.sections = self._parse_sections(content)
        self.rules = self._extract_all_rules()

        return self.sections

    def _parse_sections(self, content: str) -> List[Section]:
        """Parse markdown into sections."""
        sections = []

        # Match section headers: ## SECTION X: Name
        section_pattern = r"^## SECTION (\d+): (.+)$"
        rule_pattern = r"^### Rule (\d+): (.+)$"

        lines = content.split("\n")
        current_section: Optional[Section] = None
        current_rule: Optional[Rule] = None
        current_content: List[str] = []

        for i, line in enumerate(lines):
            # Check for section header
            section_match = re.match(section_pattern, line, re.MULTILINE)
            if section_match:
                # Save previous rule if exists
                if current_rule and current_content:
                    current_rule.content = "\n".join(current_content).strip()
                    self._extract_rule_metadata(current_rule)
                    if current_section:
                        current_section.rules.append(current_rule)

                # Save previous section
                if current_section:
                    sections.append(current_section)

                # Start new section
                section_num = int(section_match.group(1))
                section_name = section_match.group(2).strip()
                current_section = Section(
                    number=section_num,
                    name=section_name,
                    description=""
                )
                current_rule = None
                current_content = []
                continue

            # Check for rule header
            rule_match = re.match(rule_pattern, line, re.MULTILINE)
            if rule_match:
                # Save previous rule
                if current_rule and current_content:
                    current_rule.content = "\n".join(current_content).strip()
                    self._extract_rule_metadata(current_rule)
                    if current_section:
                        current_section.rules.append(current_rule)

                # Start new rule
                rule_num = int(rule_match.group(1))
                rule_name = rule_match.group(2).strip()
                current_rule = Rule(
                    number=rule_num,
                    name=rule_name,
                    content="",
                    section=current_section.name if current_section else "Unknown"
                )
                current_content = []
                continue

            # Accumulate content
            if current_rule:
                current_content.append(line)
            elif current_section and not current_section.description:
                # First non-header content is section description
                if line.strip():
                    current_section.description = line.strip()

        # Save final rule and section
        if current_rule and current_content:
            current_rule.content = "\n".join(current_content).strip()
            self._extract_rule_metadata(current_rule)
            if current_section:
                current_section.rules.append(current_rule)

        if current_section:
            sections.append(current_section)

        return sections

    def _extract_rule_metadata(self, rule: Rule) -> None:
        """Extract keywords, priority, and agent mapping from rule content."""
        content_lower = rule.content.lower()
        name_lower = rule.name.lower()

        # Determine priority
        for priority, markers in self.PRIORITY_MARKERS.items():
            if any(marker in rule.content or marker in rule.name for marker in markers):
                rule.priority = priority
                break

        # Determine which agents this applies to
        for agent, keywords in self.AGENT_KEYWORDS.items():
            if any(kw in content_lower or kw in name_lower for kw in keywords):
                rule.applies_to.append(agent)

        # Extract keywords (significant words from rule name and content)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', rule.name + " " + rule.content[:500])
        rule.keywords = list(set(word.lower() for word in words[:20]))

    def _extract_all_rules(self) -> List[Rule]:
        """Get flat list of all rules from all sections."""
        all_rules = []
        for section in self.sections:
            all_rules.extend(section.rules)
        return all_rules

    def get_section(self, section_num: int) -> Optional[Section]:
        """Get a specific section by number."""
        for section in self.sections:
            if section.number == section_num:
                return section
        return None

    def get_rule(self, rule_num: int) -> Optional[Rule]:
        """Get a specific rule by number."""
        for rule in self.rules:
            if rule.number == rule_num:
                return rule
        return None

    def get_rules_for_agent(self, agent_type: str) -> List[Rule]:
        """Get all rules that apply to a specific agent type."""
        matching = []
        for rule in self.rules:
            if not rule.applies_to or agent_type in rule.applies_to:
                matching.append(rule)
        return matching

    def get_critical_rules(self) -> List[Rule]:
        """Get all critical priority rules."""
        return [r for r in self.rules if r.priority == "critical"]

    def search_rules(self, query: str) -> List[Rule]:
        """Search rules by keyword matching."""
        query_lower = query.lower()
        matching = []
        for rule in self.rules:
            if rule.matches_context(query_lower):
                matching.append(rule)
        return matching

    def to_prompt(
        self,
        agent_type: Optional[str] = None,
        sections: Optional[List[int]] = None,
        include_critical: bool = True,
        max_tokens: int = 4000
    ) -> str:
        """
        Generate a system prompt from relevant rules.

        Args:
            agent_type: Filter rules for specific agent
            sections: Only include specific sections
            include_critical: Always include critical rules
            max_tokens: Approximate token limit

        Returns:
            Formatted rules for system prompt
        """
        self.parse()  # Ensure parsed

        prompt_parts = ["# PROJECT RULES (From RULES.md)\n"]
        char_count = 0
        max_chars = max_tokens * 4  # Rough char to token ratio

        # Always add critical rules first
        if include_critical:
            critical = self.get_critical_rules()
            if critical:
                prompt_parts.append("\n## CRITICAL RULES (Must Follow)\n")
                for rule in critical:
                    rule_text = rule.to_prompt_format()
                    if char_count + len(rule_text) > max_chars:
                        break
                    prompt_parts.append(rule_text + "\n")
                    char_count += len(rule_text)

        # Add agent-specific rules
        if agent_type:
            agent_rules = self.get_rules_for_agent(agent_type)
            if agent_rules:
                prompt_parts.append(f"\n## Rules for {agent_type.upper()} Agent\n")
                for rule in agent_rules:
                    if rule.priority == "critical":
                        continue  # Already added
                    rule_text = rule.to_prompt_format()
                    if char_count + len(rule_text) > max_chars:
                        break
                    prompt_parts.append(rule_text + "\n")
                    char_count += len(rule_text)

        # Add section-specific rules
        if sections:
            for section_num in sections:
                section = self.get_section(section_num)
                if section:
                    prompt_parts.append(f"\n## Section {section.number}: {section.name}\n")
                    for rule in section.rules:
                        rule_text = rule.to_prompt_format()
                        if char_count + len(rule_text) > max_chars:
                            break
                        prompt_parts.append(rule_text + "\n")
                        char_count += len(rule_text)

        return "\n".join(prompt_parts)

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of parsed rules."""
        self.parse()

        return {
            "file_path": str(self.rules_path),
            "file_hash": self._file_hash,
            "total_sections": len(self.sections),
            "total_rules": len(self.rules),
            "critical_rules": len(self.get_critical_rules()),
            "rules_by_priority": {
                "critical": len([r for r in self.rules if r.priority == "critical"]),
                "high": len([r for r in self.rules if r.priority == "high"]),
                "normal": len([r for r in self.rules if r.priority == "normal"]),
                "low": len([r for r in self.rules if r.priority == "low"]),
            },
            "rules_by_agent": {
                agent: len(self.get_rules_for_agent(agent))
                for agent in self.AGENT_KEYWORDS.keys()
            }
        }


# Convenience function for quick access
_parser_instance: Optional[RulesParser] = None

def get_rules_parser() -> RulesParser:
    """Get singleton rules parser instance."""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = RulesParser()
    return _parser_instance
