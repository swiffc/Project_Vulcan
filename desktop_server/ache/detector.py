"""
ACHE Model Detector
Phase 24.1.2 - ACHE model detection (custom property/filename)

Detects if a SolidWorks model is an ACHE (Air Cooled Heat Exchanger)
based on:
- Custom properties (Project Type, Equipment Type, etc.)
- Filename patterns (ACHE-, ACU-, FIN-, etc.)
- Assembly structure (header boxes, tube bundles, fans)
"""

import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Any
from enum import Enum

logger = logging.getLogger("vulcan.ache.detector")


class ACHEComponentType(str, Enum):
    """Types of ACHE components."""
    HEADER_BOX = "header_box"
    TUBE_BUNDLE = "tube_bundle"
    FAN = "fan"
    STRUCTURE = "structure"
    PLENUM = "plenum"
    WALKWAY = "walkway"
    LADDER = "ladder"
    HANDRAIL = "handrail"
    NOZZLE = "nozzle"
    UNKNOWN = "unknown"


@dataclass
class ACHEDetectionResult:
    """Result of ACHE model detection."""
    is_ache: bool
    confidence: float  # 0.0 - 1.0
    component_type: ACHEComponentType
    detection_reasons: List[str]
    api_661_applicable: bool
    suggested_validators: List[str]


class ACHEModelDetector:
    """
    Detects if a model is ACHE-related and classifies component type.

    Implements Phase 24.1.2: ACHE model detection

    Detection methods:
    1. Custom property matching (highest confidence)
    2. Filename pattern matching
    3. Assembly component analysis
    4. Feature/geometry analysis
    """

    # Custom properties that indicate ACHE
    ACHE_PROPERTY_INDICATORS = {
        "Project Type": ["ACHE", "AIR COOLED", "FIN FAN", "ACC"],
        "Equipment Type": ["HEAT EXCHANGER", "COOLER", "CONDENSER"],
        "Standard": ["API 661", "ISO 13706"],
        "ACHE Type": ["*"],  # Any value means it's ACHE
        "Bundle Type": ["*"],
    }

    # Filename patterns that indicate ACHE
    ACHE_FILENAME_PATTERNS = [
        r"^ACHE[-_]",           # ACHE-001, ACHE_HEADER
        r"^ACU[-_]",            # ACU-001 (Air Cooled Unit)
        r"^FIN[-_]?FAN",        # FIN-FAN, FINFAN
        r"^ACC[-_]",            # ACC-001 (Air Cooled Condenser)
        r"HEADER[-_]?BOX",      # HEADER-BOX, HEADERBOX
        r"TUBE[-_]?BUNDLE",     # TUBE-BUNDLE, TUBEBUNDLE
        r"PLENUM",              # PLENUM-001
        r"^[MS][-_]\d+",        # M-001 (Mechanical), S-001 (Structural)
    ]

    # Component classification keywords
    COMPONENT_KEYWORDS = {
        ACHEComponentType.HEADER_BOX: [
            "header", "plug", "cover plate", "bonnet", "partition"
        ],
        ACHEComponentType.TUBE_BUNDLE: [
            "bundle", "tube", "fin", "finned tube", "tubesheet"
        ],
        ACHEComponentType.FAN: [
            "fan", "blade", "hub", "ring", "motor", "drive"
        ],
        ACHEComponentType.STRUCTURE: [
            "structure", "column", "beam", "brace", "frame", "support"
        ],
        ACHEComponentType.PLENUM: [
            "plenum", "chamber", "air box"
        ],
        ACHEComponentType.WALKWAY: [
            "walkway", "platform", "grating", "floor"
        ],
        ACHEComponentType.LADDER: [
            "ladder", "cage", "rung", "stringer"
        ],
        ACHEComponentType.HANDRAIL: [
            "handrail", "rail", "toe", "kickplate", "gate"
        ],
        ACHEComponentType.NOZZLE: [
            "nozzle", "flange", "inlet", "outlet", "vent", "drain"
        ],
    }

    def __init__(self):
        """Initialize the detector."""
        self._compiled_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.ACHE_FILENAME_PATTERNS
        ]

    def detect(
        self,
        filepath: str,
        custom_properties: Dict[str, Any],
        component_names: Optional[List[str]] = None
    ) -> ACHEDetectionResult:
        """
        Detect if model is ACHE-related.

        Args:
            filepath: Full path to model file
            custom_properties: Dict of custom properties
            component_names: List of component names (for assemblies)

        Returns:
            ACHEDetectionResult with detection details
        """
        reasons = []
        confidence = 0.0

        # Check custom properties (highest weight)
        prop_match, prop_reasons = self._check_properties(custom_properties)
        if prop_match:
            confidence += 0.5
            reasons.extend(prop_reasons)

        # Check filename pattern
        filename_match, filename_reason = self._check_filename(filepath)
        if filename_match:
            confidence += 0.3
            reasons.append(filename_reason)

        # Check component names (for assemblies)
        if component_names:
            comp_match, comp_reasons = self._check_components(component_names)
            if comp_match:
                confidence += 0.2
                reasons.extend(comp_reasons)

        # Determine component type
        component_type = self._classify_component(
            filepath, custom_properties, component_names or []
        )

        # Determine if API 661 applies
        api_661_applicable = self._check_api_661_applicability(
            custom_properties, component_type
        )

        # Suggest validators
        validators = self._suggest_validators(component_type, api_661_applicable)

        is_ache = confidence >= 0.3

        if is_ache:
            logger.info(f"Detected ACHE model: {filepath} (confidence: {confidence:.0%})")
        else:
            logger.debug(f"Not ACHE: {filepath}")

        return ACHEDetectionResult(
            is_ache=is_ache,
            confidence=min(confidence, 1.0),
            component_type=component_type,
            detection_reasons=reasons,
            api_661_applicable=api_661_applicable,
            suggested_validators=validators,
        )

    def _check_properties(
        self, properties: Dict[str, Any]
    ) -> tuple[bool, List[str]]:
        """Check custom properties for ACHE indicators."""
        reasons = []

        for prop_name, valid_values in self.ACHE_PROPERTY_INDICATORS.items():
            if prop_name in properties:
                prop_value = str(properties[prop_name]).upper()
                if "*" in valid_values:
                    # Any value is valid
                    reasons.append(f"Property '{prop_name}' present: {prop_value}")
                else:
                    for valid in valid_values:
                        if valid.upper() in prop_value:
                            reasons.append(f"Property '{prop_name}' = '{prop_value}'")
                            break

        return len(reasons) > 0, reasons

    def _check_filename(self, filepath: str) -> tuple[bool, str]:
        """Check filename for ACHE patterns."""
        import os
        filename = os.path.basename(filepath)

        for pattern in self._compiled_patterns:
            if pattern.search(filename):
                return True, f"Filename matches ACHE pattern: {filename}"

        return False, ""

    def _check_components(
        self, component_names: List[str]
    ) -> tuple[bool, List[str]]:
        """Check assembly component names for ACHE indicators."""
        reasons = []
        ache_keywords = ["header", "bundle", "tube", "fan", "plenum", "ache"]

        for name in component_names:
            name_lower = name.lower()
            for keyword in ache_keywords:
                if keyword in name_lower:
                    reasons.append(f"Component '{name}' indicates ACHE")
                    break

        return len(reasons) >= 2, reasons  # Need at least 2 matching components

    def _classify_component(
        self,
        filepath: str,
        properties: Dict[str, Any],
        component_names: List[str]
    ) -> ACHEComponentType:
        """Classify the type of ACHE component."""
        import os
        filename = os.path.basename(filepath).lower()

        # Check filename and properties against keywords
        all_text = filename + " " + " ".join(str(v) for v in properties.values())
        all_text = all_text.lower()

        for comp_type, keywords in self.COMPONENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in all_text:
                    return comp_type

        return ACHEComponentType.UNKNOWN

    def _check_api_661_applicability(
        self,
        properties: Dict[str, Any],
        component_type: ACHEComponentType
    ) -> bool:
        """Check if API 661 applies to this model."""
        # API 661 applies to main ACHE components
        api_661_components = {
            ACHEComponentType.HEADER_BOX,
            ACHEComponentType.TUBE_BUNDLE,
            ACHEComponentType.FAN,
            ACHEComponentType.NOZZLE,
        }

        if component_type in api_661_components:
            return True

        # Check for explicit standard reference
        standard = properties.get("Standard", "").upper()
        if "API 661" in standard or "ISO 13706" in standard:
            return True

        return False

    def _suggest_validators(
        self,
        component_type: ACHEComponentType,
        api_661_applicable: bool
    ) -> List[str]:
        """Suggest relevant validators for the component."""
        validators = []

        if api_661_applicable:
            validators.append("/phase25/check-api661-full")

        # Component-specific validators
        component_validators = {
            ACHEComponentType.HEADER_BOX: [
                "/phase25/check-asme-viii",
                "/phase25/check-gdt",
            ],
            ACHEComponentType.TUBE_BUNDLE: [
                "/phase25/check-tema",
                "/phase25/check-materials",
            ],
            ACHEComponentType.FAN: [
                "/phase25/check-nema-motor",
            ],
            ACHEComponentType.STRUCTURE: [
                "/phase25/check-structural",
                "/phase25/check-member-capacity",
            ],
            ACHEComponentType.WALKWAY: [
                "/phase25/check-osha",
                "/phase25/check-rigging",
            ],
            ACHEComponentType.LADDER: [
                "/phase25/check-osha",
            ],
            ACHEComponentType.HANDRAIL: [
                "/phase25/check-osha",
            ],
            ACHEComponentType.NOZZLE: [
                "/phase25/check-weld",
                "/phase25/check-gdt",
            ],
        }

        if component_type in component_validators:
            validators.extend(component_validators[component_type])

        # Always include these
        validators.append("/phase25/check-documentation")
        validators.append("/phase25/check-bom")

        return list(dict.fromkeys(validators))  # Remove duplicates, preserve order

    def get_detection_config(self) -> Dict[str, Any]:
        """Get current detection configuration."""
        return {
            "property_indicators": self.ACHE_PROPERTY_INDICATORS,
            "filename_patterns": self.ACHE_FILENAME_PATTERNS,
            "component_keywords": {
                k.value: v for k, v in self.COMPONENT_KEYWORDS.items()
            },
        }
