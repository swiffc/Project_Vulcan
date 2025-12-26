"""
Configurable Rules Engine
=========================
Externalizes validator rules to YAML/JSON configuration files.

Features:
- Load rules from config files
- Dynamic rule evaluation
- Rule versioning and overrides
- Standard-specific rule sets
"""

import json
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum
from functools import lru_cache
import re


class RuleSeverity(str, Enum):
    """Rule violation severity levels."""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class RuleOperator(str, Enum):
    """Comparison operators for rules."""
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"
    IN = "in"
    NOT_IN = "not_in"
    BETWEEN = "between"
    MATCHES = "matches"  # Regex
    EXISTS = "exists"


@dataclass
class ValidationRule:
    """A single validation rule."""
    id: str
    name: str
    description: str
    standard: str
    section: Optional[str]
    severity: RuleSeverity
    field: str
    operator: RuleOperator
    value: Any
    message: str
    suggestion: Optional[str] = None
    enabled: bool = True
    version: str = "1.0"
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "standard": self.standard,
            "section": self.section,
            "severity": self.severity.value if isinstance(self.severity, RuleSeverity) else self.severity,
            "field": self.field,
            "operator": self.operator.value if isinstance(self.operator, RuleOperator) else self.operator,
            "value": self.value,
            "message": self.message,
            "suggestion": self.suggestion,
            "enabled": self.enabled,
            "version": self.version,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValidationRule":
        """Create rule from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            standard=data.get("standard", ""),
            section=data.get("section"),
            severity=RuleSeverity(data.get("severity", "warning")),
            field=data["field"],
            operator=RuleOperator(data["operator"]),
            value=data["value"],
            message=data["message"],
            suggestion=data.get("suggestion"),
            enabled=data.get("enabled", True),
            version=data.get("version", "1.0"),
            tags=data.get("tags", []),
        )


@dataclass
class RuleViolation:
    """Result of a rule evaluation."""
    rule_id: str
    rule_name: str
    severity: RuleSeverity
    message: str
    suggestion: Optional[str]
    field: str
    actual_value: Any
    expected_value: Any
    standard_reference: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "severity": self.severity.value,
            "message": self.message,
            "suggestion": self.suggestion,
            "field": self.field,
            "actual_value": self.actual_value,
            "expected_value": self.expected_value,
            "standard_reference": self.standard_reference,
        }


class RulesEngine:
    """
    Configurable validation rules engine.

    Features:
    - Load rules from YAML/JSON files
    - Evaluate rules against data
    - Filter by standard, severity, tags
    - Rule versioning
    """

    def __init__(self, rules_dir: Optional[Path] = None):
        """
        Initialize rules engine.

        Args:
            rules_dir: Directory containing rule configuration files
        """
        if rules_dir:
            self.rules_dir = Path(rules_dir)
        else:
            self.rules_dir = Path(__file__).parent / "rules"

        self._rules: Dict[str, ValidationRule] = {}
        self._rules_by_standard: Dict[str, List[ValidationRule]] = {}
        self._rules_by_tag: Dict[str, List[ValidationRule]] = {}

        # Load built-in rules
        self._load_builtin_rules()

        # Load external rules if directory exists
        if self.rules_dir.exists():
            self._load_external_rules()

    def _load_builtin_rules(self):
        """Load built-in engineering rules."""
        builtin_rules = [
            # AISC Bolt Spacing Rules
            ValidationRule(
                id="AISC-J3.3-001",
                name="Minimum Bolt Spacing",
                description="Minimum distance between bolt centers",
                standard="AISC 360-16",
                section="J3.3",
                severity=RuleSeverity.ERROR,
                field="bolt_spacing",
                operator=RuleOperator.GREATER_THAN_OR_EQUAL,
                value={"multiplier": 2.67, "base_field": "bolt_diameter"},
                message="Bolt spacing must be at least 2.67 times bolt diameter",
                suggestion="Increase spacing or use smaller bolts",
                tags=["structural", "bolts", "spacing"]
            ),
            ValidationRule(
                id="AISC-J3.4-001",
                name="Minimum Edge Distance (Rolled)",
                description="Minimum edge distance for rolled edges",
                standard="AISC 360-16",
                section="J3.4",
                severity=RuleSeverity.ERROR,
                field="edge_distance",
                operator=RuleOperator.GREATER_THAN_OR_EQUAL,
                value={"lookup": "edge_distance_table", "edge_type": "rolled"},
                message="Edge distance less than minimum for rolled edge",
                suggestion="Increase edge distance or use smaller bolt",
                tags=["structural", "bolts", "edge_distance"]
            ),
            # AWS Weld Rules
            ValidationRule(
                id="AWS-D1.1-5.8-001",
                name="Minimum Fillet Weld Size",
                description="Minimum fillet weld size based on thicker plate",
                standard="AWS D1.1",
                section="Table 5.8",
                severity=RuleSeverity.ERROR,
                field="fillet_weld_size",
                operator=RuleOperator.GREATER_THAN_OR_EQUAL,
                value={"lookup": "fillet_weld_table"},
                message="Fillet weld size below minimum for base metal thickness",
                suggestion="Increase weld size per AWS D1.1 Table 5.8",
                tags=["welding", "fillet", "size"]
            ),
            # ASME B31.3 Pipe Rules
            ValidationRule(
                id="ASME-B31.3-304.1.2-001",
                name="Minimum Pipe Wall Thickness",
                description="Minimum wall thickness for pressure containment",
                standard="ASME B31.3",
                section="304.1.2",
                severity=RuleSeverity.CRITICAL,
                field="wall_thickness",
                operator=RuleOperator.GREATER_THAN_OR_EQUAL,
                value={"formula": "pressure_wall_thickness"},
                message="Pipe wall thickness insufficient for design pressure",
                suggestion="Use heavier schedule pipe or reduce design pressure",
                tags=["piping", "pressure", "wall_thickness"]
            ),
            # Handling Rules
            ValidationRule(
                id="HPC-LIFT-001",
                name="Lifting Lug Required",
                description="Lifting lugs required for heavy components",
                standard="HPC Standards",
                section="Lifting",
                severity=RuleSeverity.ERROR,
                field="weight_lbs",
                operator=RuleOperator.LESS_THAN,
                value=500,  # If >= 500 lbs, needs lifting lugs
                message="Component over 500 lbs requires lifting lugs",
                suggestion="Add certified lifting lugs per HPC standard",
                tags=["handling", "lifting", "safety"]
            ),
            ValidationRule(
                id="HPC-LIFT-002",
                name="CG Marking Required",
                description="Center of gravity marking required for heavy lifts",
                standard="HPC Standards",
                section="Marking",
                severity=RuleSeverity.WARNING,
                field="weight_lbs",
                operator=RuleOperator.LESS_THAN,
                value=1000,
                message="Component over 1000 lbs requires CG marking",
                suggestion="Mark center of gravity location on drawing",
                tags=["handling", "marking", "safety"]
            ),
            # Fabrication Rules
            ValidationRule(
                id="FAB-HOLE-001",
                name="Minimum Hole Diameter",
                description="Minimum hole size for laser/plasma cutting",
                standard="Fabrication Best Practice",
                section=None,
                severity=RuleSeverity.WARNING,
                field="hole_diameter",
                operator=RuleOperator.GREATER_THAN_OR_EQUAL,
                value={"multiplier": 1.0, "base_field": "plate_thickness"},
                message="Hole diameter should be at least 1x plate thickness",
                suggestion="Increase hole size or use drilling operation",
                tags=["fabrication", "holes", "laser"]
            ),
            ValidationRule(
                id="FAB-BEND-001",
                name="Minimum Bend Radius",
                description="Minimum inside bend radius for sheet metal",
                standard="Fabrication Best Practice",
                section=None,
                severity=RuleSeverity.ERROR,
                field="bend_radius",
                operator=RuleOperator.GREATER_THAN_OR_EQUAL,
                value={"multiplier": 1.0, "base_field": "material_thickness"},
                message="Bend radius too tight for material thickness",
                suggestion="Increase bend radius to prevent cracking",
                tags=["fabrication", "bending", "sheet_metal"]
            ),
            # GDT Rules
            ValidationRule(
                id="GDT-POS-001",
                name="Position Tolerance Achievability",
                description="Position tolerance must be achievable by machining process",
                standard="ASME Y14.5-2018",
                section="7.2",
                severity=RuleSeverity.WARNING,
                field="position_tolerance",
                operator=RuleOperator.GREATER_THAN_OR_EQUAL,
                value=0.005,  # 0.005" typical machining capability
                message="Position tolerance tighter than typical machining capability",
                suggestion="Consider if tight tolerance is truly required",
                tags=["gdt", "position", "tolerance"]
            ),
        ]

        for rule in builtin_rules:
            self.add_rule(rule)

    def _load_external_rules(self):
        """Load rules from external YAML/JSON files."""
        for filepath in self.rules_dir.glob("*.yaml"):
            self._load_rules_file(filepath)
        for filepath in self.rules_dir.glob("*.yml"):
            self._load_rules_file(filepath)
        for filepath in self.rules_dir.glob("*.json"):
            self._load_rules_file(filepath)

    def _load_rules_file(self, filepath: Path):
        """Load rules from a single file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                if filepath.suffix in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)

            rules_list = data.get("rules", [])
            for rule_data in rules_list:
                try:
                    rule = ValidationRule.from_dict(rule_data)
                    self.add_rule(rule)
                except Exception as e:
                    print(f"Error loading rule from {filepath}: {e}")
        except Exception as e:
            print(f"Error loading rules file {filepath}: {e}")

    def add_rule(self, rule: ValidationRule):
        """Add a rule to the engine."""
        self._rules[rule.id] = rule

        # Index by standard
        if rule.standard not in self._rules_by_standard:
            self._rules_by_standard[rule.standard] = []
        self._rules_by_standard[rule.standard].append(rule)

        # Index by tags
        for tag in rule.tags:
            if tag not in self._rules_by_tag:
                self._rules_by_tag[tag] = []
            self._rules_by_tag[tag].append(rule)

    def get_rule(self, rule_id: str) -> Optional[ValidationRule]:
        """Get a rule by ID."""
        return self._rules.get(rule_id)

    def get_rules_by_standard(self, standard: str) -> List[ValidationRule]:
        """Get all rules for a specific standard."""
        return self._rules_by_standard.get(standard, [])

    def get_rules_by_tag(self, tag: str) -> List[ValidationRule]:
        """Get all rules with a specific tag."""
        return self._rules_by_tag.get(tag, [])

    def get_rules_by_severity(self, severity: RuleSeverity) -> List[ValidationRule]:
        """Get all rules of a specific severity."""
        return [r for r in self._rules.values() if r.severity == severity]

    def list_standards(self) -> List[str]:
        """List all standards with rules."""
        return list(self._rules_by_standard.keys())

    def list_tags(self) -> List[str]:
        """List all rule tags."""
        return list(self._rules_by_tag.keys())

    # ==================== RULE EVALUATION ====================

    def evaluate(self, data: Dict[str, Any],
                 rules: Optional[List[ValidationRule]] = None,
                 standard: Optional[str] = None,
                 tags: Optional[List[str]] = None) -> List[RuleViolation]:
        """
        Evaluate rules against data.

        Args:
            data: Dictionary of field values to check
            rules: Specific rules to evaluate (optional)
            standard: Filter by standard (optional)
            tags: Filter by tags (optional)

        Returns:
            List of RuleViolation objects for failed rules
        """
        violations: List[RuleViolation] = []

        # Determine which rules to evaluate
        if rules:
            rules_to_check = rules
        elif standard:
            rules_to_check = self.get_rules_by_standard(standard)
        elif tags:
            rules_to_check = []
            for tag in tags:
                rules_to_check.extend(self.get_rules_by_tag(tag))
            rules_to_check = list(set(rules_to_check))  # Remove duplicates
        else:
            rules_to_check = list(self._rules.values())

        # Evaluate each rule
        for rule in rules_to_check:
            if not rule.enabled:
                continue

            violation = self._evaluate_rule(rule, data)
            if violation:
                violations.append(violation)

        return violations

    def _evaluate_rule(self, rule: ValidationRule, data: Dict[str, Any]) -> Optional[RuleViolation]:
        """Evaluate a single rule against data."""
        # Get the field value
        field_value = self._get_field_value(rule.field, data)
        if field_value is None:
            return None  # Field not present, skip rule

        # Get the comparison value
        expected = self._resolve_value(rule.value, data)

        # Evaluate the operator
        passed = self._evaluate_operator(rule.operator, field_value, expected)

        if not passed:
            return RuleViolation(
                rule_id=rule.id,
                rule_name=rule.name,
                severity=rule.severity,
                message=rule.message,
                suggestion=rule.suggestion,
                field=rule.field,
                actual_value=field_value,
                expected_value=expected,
                standard_reference=f"{rule.standard} {rule.section}" if rule.section else rule.standard
            )

        return None

    def _get_field_value(self, field: str, data: Dict[str, Any]) -> Any:
        """Get a field value from data, supporting nested paths."""
        if "." in field:
            parts = field.split(".")
            value = data
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part)
                else:
                    return None
            return value
        return data.get(field)

    def _resolve_value(self, value: Any, data: Dict[str, Any]) -> Any:
        """Resolve a rule value, handling dynamic references."""
        if isinstance(value, dict):
            # Multiplier-based value
            if "multiplier" in value and "base_field" in value:
                base_value = self._get_field_value(value["base_field"], data)
                if base_value is not None:
                    return value["multiplier"] * base_value
            # Lookup table
            if "lookup" in value:
                return self._lookup_value(value["lookup"], data)
            # Formula
            if "formula" in value:
                return self._calculate_formula(value["formula"], data)

        return value

    def _lookup_value(self, table_name: str, data: Dict[str, Any]) -> Any:
        """Look up a value from a reference table."""
        # Edge distance table
        if table_name == "edge_distance_table":
            bolt_size = data.get("bolt_diameter", 0.75)
            edge_type = data.get("edge_type", "rolled")
            # AISC Table J3.4 values
            edge_distances = {
                0.5: {"rolled": 0.75, "sheared": 0.875},
                0.625: {"rolled": 0.875, "sheared": 1.125},
                0.75: {"rolled": 1.0, "sheared": 1.25},
                0.875: {"rolled": 1.125, "sheared": 1.5},
                1.0: {"rolled": 1.25, "sheared": 1.75},
            }
            return edge_distances.get(bolt_size, {}).get(edge_type, 1.0)

        # Fillet weld table (AWS D1.1 Table 5.8)
        if table_name == "fillet_weld_table":
            thickness = data.get("base_metal_thickness", 0.5)
            if thickness <= 0.25:
                return 0.125  # 1/8"
            elif thickness <= 0.5:
                return 0.1875  # 3/16"
            elif thickness <= 0.75:
                return 0.25  # 1/4"
            else:
                return 0.3125  # 5/16"

        return None

    def _calculate_formula(self, formula_name: str, data: Dict[str, Any]) -> Any:
        """Calculate a formula-based value."""
        if formula_name == "pressure_wall_thickness":
            # ASME B31.3 Equation 3a
            P = data.get("design_pressure", 150)
            D = data.get("pipe_od", 4.5)
            S = data.get("allowable_stress", 20000)
            E = data.get("joint_factor", 1.0)
            W = data.get("weld_factor", 1.0)
            Y = data.get("y_coefficient", 0.4)
            c = data.get("corrosion_allowance", 0.0625)

            t = (P * D) / (2 * (S * E * W + P * Y)) + c
            return t

        return None

    def _evaluate_operator(self, operator: RuleOperator, actual: Any, expected: Any) -> bool:
        """Evaluate a comparison operator."""
        try:
            if operator == RuleOperator.EQUALS:
                return actual == expected
            elif operator == RuleOperator.NOT_EQUALS:
                return actual != expected
            elif operator == RuleOperator.GREATER_THAN:
                return actual > expected
            elif operator == RuleOperator.GREATER_THAN_OR_EQUAL:
                return actual >= expected
            elif operator == RuleOperator.LESS_THAN:
                return actual < expected
            elif operator == RuleOperator.LESS_THAN_OR_EQUAL:
                return actual <= expected
            elif operator == RuleOperator.IN:
                return actual in expected
            elif operator == RuleOperator.NOT_IN:
                return actual not in expected
            elif operator == RuleOperator.BETWEEN:
                return expected[0] <= actual <= expected[1]
            elif operator == RuleOperator.MATCHES:
                return bool(re.match(expected, str(actual)))
            elif operator == RuleOperator.EXISTS:
                return actual is not None
        except (TypeError, ValueError):
            return False
        return False

    # ==================== EXPORT / SERIALIZATION ====================

    def export_rules(self, format: str = "yaml") -> str:
        """Export all rules to YAML or JSON string."""
        rules_data = {"rules": [rule.to_dict() for rule in self._rules.values()]}

        if format == "yaml":
            return yaml.dump(rules_data, default_flow_style=False, sort_keys=False)
        else:
            return json.dumps(rules_data, indent=2)

    def save_rules(self, filepath: Path):
        """Save rules to a file."""
        suffix = filepath.suffix.lower()
        content = self.export_rules("yaml" if suffix in [".yaml", ".yml"] else "json")

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of loaded rules."""
        return {
            "total_rules": len(self._rules),
            "by_standard": {std: len(rules) for std, rules in self._rules_by_standard.items()},
            "by_severity": {
                "critical": len(self.get_rules_by_severity(RuleSeverity.CRITICAL)),
                "error": len(self.get_rules_by_severity(RuleSeverity.ERROR)),
                "warning": len(self.get_rules_by_severity(RuleSeverity.WARNING)),
                "info": len(self.get_rules_by_severity(RuleSeverity.INFO)),
            },
            "tags": list(self._rules_by_tag.keys()),
        }
